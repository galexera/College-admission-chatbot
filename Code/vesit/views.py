from django.shortcuts import render
import os
from django.conf import settings
from django.shortcuts import render
from .models import UserConversation,Webdata
from django.http import JsonResponse
import httplib2
from bs4 import BeautifulSoup,SoupStrainer
"""
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string
from textblob import TextBlob
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import pandas as pd
import pickle
import random
from textblob import TextBlob
import json
"""
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
from nltk.corpus import stopwords
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import pandas as pd
import pickle
import random
from textblob import TextBlob
import json
import re

file_path = os.path.join(settings.STATIC_ROOT, 'swarangi.json')

with open(file_path, 'r',encoding="utf-8") as json_data:
    intents = json.load(json_data)

nltk.download('punkt')
words = []
classes = []
documents = []
ignore_words = ['?']
# loop through each sentence in our intents patterns
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenize each word in the sentence
        w = nltk.word_tokenize(pattern)
        # add to our words list
        words.extend(w)
        # add to documents in our corpus
        documents.append((w, intent['tag']))
        # add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# sort classes
classes = sorted(list(set(classes)))

# documents = combination between patterns and intents
print (len(documents), "documents")
# classes = intents
print (len(classes), "classes", classes)
# words = all words, vocabulary
print (len(words), "unique stemmed words", words)

# create our training data
training = []
# create an empty array for our output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    # stem each word - create base word, in attempt to represent related words
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # create our bag of words array with 1, if word match found in current pattern
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    
    # output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    
    training.append([bag, output_row])

# shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training)

# create train and test lists. X - patterns, Y - intents
train_x = list(training[:,0])
train_y = list(training[:,1])

# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                #if show_details:
                 #   print ("found in bag: %s" % w)

    return(np.array(bag))

context = {}

ERROR_THRESHOLD = 0.7

def classify(sentence):
  
    p=bow(sentence, words)
    # generate probabilities from the model
    inputvar = pd.DataFrame([p], dtype=float, index=['input'])
    results = model.predict([inputvar])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list

def response(sentence, userID='123', show_details=False):
    resultr=TextBlob(sentence)
    test_str=str(resultr.correct())
    print("Did you mean :",test_str)
    results = classify(test_str)
    
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # a random response from the intent
                        final_answer=random.choice(i['responses'])
                        print("Pooja"+random.choice(i['responses']))
                        return str(final_answer)
                        #ChatbotResponse.append(random.choice(i['responses']))
                        #return render(request,'vesitadmission.html',{'chatbotMsg':UserMessage,'userMsg':ChatbotResponse,'limit':len(UserMessage),'data':zip(UserMessage,ChatbotResponse),'range':range(0,10)})

            results.pop(0)

classify('scholarship')
# Create your views here.

UserMessage=[]
ChatbotResponse=[]
UserMessageTime=[]
linkss="Pooja"

def vesitShow(request):
        return render(request,'vesitadmission.html')

def MessageSends(request):
    msg=request.GET['userMsg']
    user_time=request.GET['submissionDate']
    UserMessage.append(msg)
    lemm=WordNetLemmatizer()
    resultr=TextBlob(msg)
    test_str=str(resultr.correct())
    print(test_str)
    stop_words = set(stopwords.words('english'))
    result=word_tokenize(test_str)
    filtered_words=[]
    for word in result:
        if word not in stop_words and word not in string.punctuation:
            filtered_words.append(lemm.lemmatize(word,pos="v"))
    #print(filtered_words)
    print("I thought you were saying about:",filtered_words)
    final_msg="I thought you were saying about: "
    for i in range(0,len(filtered_words)):
        final_msg=final_msg+filtered_words[i]+","
    ChatbotResponse.append(final_msg)
    return render(request,'vesitadmission.html',{'chatbotMsg':UserMessage,'userMsg':ChatbotResponse,'limit':len(UserMessage),'data':zip(UserMessage,ChatbotResponse,UserMessageTime),'range':range(0,10)})

def FormSendWeb():
    http = httplib2.Http()
    status, response = http.request('http://127.0.0.1:8080/')
    for link in BeautifulSoup(response, 'html.parser',parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href'):
            print(link['href'])
            entry_table=Webdata(title="VESIT",address=link['href'])
            entry_table.save()
    mycontent=Webdata.objects.all()
    return mycontent

def VesitChatbot(request):
    msg=request.POST['UserMsg']
    user_time=request.POST.get('submissionDate')
    UserMessageTime.append(user_time)
    UserMessage.append(msg)
    ans=response(msg.lower())
    print("My answer:"+str(ans))
    if(ans!=None):
        ChatbotResponse.append(ans)
        #webdatas=FormSendWeb()
        '''if ans=="Kay pan bolu che":
         if Webdata.objects.filter(address=msg):
            print("SOmething found")
            ans="true"
        '''
        new_obj=UserConversation(UserQuestion=msg,ChatbotResponse=ans)
        new_obj.save()
        mycontent=UserConversation.objects.all()
    else:
        flag=0
        #webdatas=FormSendWeb()
        sentence_words = clean_up_sentence(msg)
        print(sentence_words)
        for word in reversed(sentence_words):
           if Webdata.objects.filter(address__contains=word).all():
                results=Webdata.objects.filter(address__contains=word).all()
                print("For Word:"+word)
                print("SOmething found")
                ans=results[0].address
                print("Error aave che")
                flag=1
                break
        if flag==0:
            ans="Please tell something else, I am unable to understand your question.If you require any information about the college,please visit our website http://vesit.ves.ac.in."
    print(user_time)
    return JsonResponse({'UserQ':msg,'ChatbotA':ans,'userTime':user_time},status=200)
    #return render(request,'vesitadmission.html',{'chatbotMsg':UserMessage,'userMsg':ChatbotResponse,'userTime':UserMessageTime,'limit':len(UserMessage),'data':zip(UserMessage,ChatbotResponse,UserMessageTime),'range':range(0,10),'datas':"Pooja"})
