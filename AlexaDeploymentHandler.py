# coding=utf-8
import json
import random 
from AlexaBaseHandler import AlexaBaseHandler



class AlexaDeploymentHandler(AlexaBaseHandler):
    """
    Sample concrete implementation of the AlexaBaseHandler to test the
    deployment scripts and process.
    All on_ handlers call the same test response changing the request type
    spoken.
    """
    endSession = False
    fails = 0 
    wins = 0 
    
        
    with open('local_data/word_set.json') as data_file:    
        word_set = json.load(data_file)
        
    
    def __init__(self):
        super(self.__class__, self).__init__()
   

    def on_launch(self, launch_request, session):
        """ If we wanted to initialize the session to have some attributes we could
        add those here
        """
        session_attributes = {}
        card_title = "Word Connect" 
        speech_output = "Word Connect ! Start a game or ask for help"
        card_output = speech_output
        reprompt_text = ""
        should_end_session = False
        self.endSession = False
        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
        return self._build_response(session_attributes, speechlet)

    def on_session_started(self, session_started_request, session):
        print "on_session_started requestId=" + session_started_request['requestId']+ ", sessionId=" + session['sessionId']
          
    def on_intent(self, intent_request, session):
        return self._manage_intents(intent_request,session)

    def on_session_ended(self, session_end_request, session):
        session_attributes = {}
        card_title = "Bye Bye" 
        speech_output = "Word connect ended"
        card_output = speech_output
        reprompt_text = ""
        should_end_session = True
        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
        return self._build_response(session_attributes, speechlet)

    def _manage_intents(self, intent_request, session):
        if 'attributes' in session.keys():
            session_attributes = session['attributes']
        else:
            session_attributes = {}
        
        try:
            intent  = intent_request['intent']['name']
            print intent
            if intent == "StartGameIntent":
                #print intent_request['intent']['slots']['team']['resolutions']
                question_word = self.get_new_word([])
                session_attributes['QuestionWord'] = question_word
                print "Question Word - " + question_word
                speechlet = self.start_game(question_word)
            elif intent == "AnswerIntent":
                answer_word = intent_request['intent']['slots']['answer']['value']
                question_word = session_attributes['QuestionWord']
                used_word_list = []
                if 'UsedWords' in session_attributes.keys():
                    used_word_list = session_attributes['UsedWords'] 
                new_word = self.get_new_word(used_word_list)
                if new_word is None:
                    speechlet = self.no_words_available()
                else:
                    if 'Fails' in session_attributes.keys():
                        self.fails = int(session_attributes['Fails'])
                    if 'Wins' in session_attributes.keys():
                        self.wins = int(session_attributes['Wins'])
                        
                    speechlet = self.get_answer(question_word,answer_word, new_word)
                    used_word_list.append(question_word)
                    session_attributes['UsedWords']  =  used_word_list
                    session_attributes['QuestionWord'] = new_word 
                    session_attributes['Fails'] = self.fails
                    session_attributes['Wins'] = self.wins
                        
            elif intent == "UnknownIntent":
                speechlet = self.get_foulSong()
            elif intent == "AMAZON.HelpIntent":
                speechlet = self.get_explanation()
            elif intent == "AMAZON.StopIntent":
                speechlet = self.stop_session()
            elif intent == "AMAZON.CancelIntent":
                speechlet = self.stop_session()
            elif intent == "UnknownIntent":
                speechlet = self.no_intent()
            else:
                print "No Intent"
                speechlet = self.no_intent()
            print "SPEECH OUTPUT: "+ str(speechlet)
        except  Exception,e: 
            speech_output = "Error"
            raise
            card_title = "We have an error"
            card_output = str(e)
            reprompt_text = ""
            should_end_session = self.endSession
            print speech_output
            speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
            #raise
            pass
        return self._build_response(session_attributes, speechlet) 
    
    def get_answer(self,question_word,answer_word, new_word):
        if self.fails > 2:
            speech_output = "Sorry you failed too often. You have to start a new game."
            card_title = "Sorry you lost"
            card_output = "After failing 3 times you have to start a new game"
            reprompt_text = ""
            should_end_session = True
        elif self.wins + self.fails == 10:
            speech_output = "You completed the game. You had " + str(self.wins) + " right answers and " + str(self.fails) + " wrong answers"
            card_title = "You completed the game"
            card_output =  "You had " + str(self.wins) + " right answers and " + str(self.fails) + " wrong answers"
            reprompt_text = ""
            should_end_session = True
        else:
            if self.check_answer(question_word, answer_word, new_word):
                speech_output = question_word+" "+answer_word+ " Correct ! Now find a connected word for " + new_word
                card_title= "Correct ! Your next word ist "+new_word
                card_output = question_word+" "+answer_word+ " Correct ! Now find a connected word for " + new_word
                self.wins += 1
            else:     
                speech_output = "Sorry"+ question_word+" "+answer_word+ " doesn't work ! Now find a connected word for " + new_word
                card_title = "Incorrect :( Your next word is " + new_word
                card_output = "Sorry "+ question_word+" "+answer_word+ " doesn't work ! Now find a connected word for " + new_word
                self.fails += 1
            reprompt_text = "What's your answer ?"
            should_end_session = False
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
      
    def no_words_available(self):
        speech_output  = "No more words available!"
        card_title = "You're done ! Congradulation"
        card_output = "No more words available at the moment."
        reprompt_text = None
        should_end_session = True
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
     
    def get_explanation(self):
        speech_output = "You need to find a connected word to a word I give you. For example If I say Key you could answer board."
        card_title = "Question Key - Your answer Board "
        card_output = speech_output
        reprompt_text = "Start a game to begin"
        should_end_session = False
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
    
    def start_game(self, question_word):
        
        speech_output = 'What connects with ' + question_word
        card_title = "Word connect: " + question_word
        card_output = "Find a Connected word for " + question_word
        reprompt_text = "What's your answer ?"
        should_end_session = False
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
    
    def stop_session(self):
        speech_output = ''
        card_title = "Word connect stopped !"
        card_output = speech_output
        reprompt_text = ""
        should_end_session = True
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

    def start_message(self):
        card_title = "Word Connect"
        card_output = "Find a connected word"
        speech_output = "Find a connected word"
        # If the user either does not reply to the welcome message or says something
        # that is not understood, they will be prompted again with this text.
        reprompt_text = "Ask to start a game to get a task"
        should_end_session = False
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
    
    def no_intent(self):
        speech_output = self.random_answer('NOINTENT')
        card_title = ""
        card_output = speech_output
        reprompt_text = ""
        should_end_session = self.endSession
        return self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)
    
    def get_new_word(self, word_set):
        word_set_current = [item for item in self.word_set.keys() if item.upper()  not in (ans.upper() for ans in word_set)]
        print word_set_current
        if not word_set_current:
            return None
        else:
            return random.choice(word_set_current)
    
    def check_answer(self, question_word, answer_word, new_word):
        check = False
        possible_answers = self.word_set[question_word]
        if answer_word.upper() in (ans.upper() for ans in possible_answers):    
            check = True
        return check
