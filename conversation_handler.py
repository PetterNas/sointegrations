git#setLanguageLevel 3;

EventData ed = getEventData();
String chatSessionId  = ed.getInputValue("chatMessage.sessionId"); //The ID for the specific chat session.
String customerText   = ed.getInputValue("chatMessage.message");   //The message sent by the user.
String specialType    = ed.getInputValue("chatMessage.specialType");
String userId         = ed.getInputValue("chatSession.userId");
String chatType       = ed.getInputValue("chatMessage.type");
String topicId        = ed.getInputValue("chatSession.topicId");
String author         = ed.getInputValue("chatMessage.author");
String botName        = "Digital assistent";
String project_id     = "norsktestbot-fihwna";


/*
On row 67 theere is a SearchEngine that will be used temporarily.
This is used to workaround TFS: 72750
*/

//Specify for which chat topic ID's your chat bot should be enabled.
if (topicId == "3"){

  ///////////////////////
  // Bot configuration //
  ///////////////////////

  //What is the name of your handover intent?
  String handOverIntent = 'X';

  //What should your bot say before handing over the session to an agent?
  String handOverMsg = 'X';

  //What is the name of your done conversation intent?
  String doneConversationIntent = 'X';

  //What should your bots good-bye message be?
  String goodBye = 'X';

  //How much delay should it be before the message is posted(In seconds)?
  Integer messageDelay = 1;

  //How much delay should it be before the second text response is sent(In seconds)?
  Integer secondMsgDelay = 2;

  ///////////////////////
  // API configuration //
  ///////////////////////

  //What is your client ID?
  String client_id = 'X';

  //What is your client secret?
  String client_secret = 'X';

  //What is your refresh token?
  String refresh_token = 'X';

  SearchEngine getLastBotMsg;
  getLastBotMsg.addField("chat_message.message");
  getLastBotMsg.addCriteria("chat_message.type", "Equals", "1");
  getLastBotMsg.addCriteria("chat_message.author", "Equals", botName);
  getLastBotMsg.addCriteria("chat_message.session_id", "Equals", chatSessionId);
  getLastBotMsg.setLimit(1);
  getLastBotMsg.addOrder("chat_message.id", false);
  getLastBotMsg.execute();
  String lastBotMsg = getLastBotMsg.getField("chat_message.message");

  //Only trigger if the message is coming from a customer and if it has not been handed over.
  if(userId == "-1" && specialType != "10" && specialType != "11" && chatType =="2" && lastBotMsg != handOverMsg){

    //Variables needed for DialogFlow to work.
    String url  = 'https://dialogflow.googleapis.com/v2/';                        //For API calls.
    String checkTokenUrl = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token='; //For validating the access token (expires after 1hour).

    //Getting the current access_token from database.
    SearchEngine accessToken;
    accessToken.addCriteria("UserPreference.prefkey", "Equals", "DialogFlow_access_token");
    accessToken.addField("UserPreference.prefvalue");
    accessToken.execute();
    String access_token = accessToken.getField("UserPreference.prefvalue"); //Taking the current access_token from DB.

    //Validating the access_token. Refreshes if invalid.
    String validate_token(String access_token){
      HTTP checkToken;
      String checkToken_return = String(checkToken.post(checkTokenUrl + access_token));
      XMLNode x3               = parseJSON(checkToken_return);
      String invalid_token     = x3.getValueFromPath("error");

      if(invalid_token != "invalid_token"){//If it is not invalid, return the current token.
        return access_token;
      }
      else{ //If it is invalid, refresh the token, save the new value, and return the new token.
        JSONBuilder refreshToken;
        refreshToken.pushObject("");
        refreshToken.addString("client_id", client_id);
        refreshToken.addString("client_secret", client_secret);
        refreshToken.addString("grant_type", "refresh_token");
        refreshToken.addString("refresh_token", refresh_token);
        refreshToken.popLevel();

        HTTP tokenPost;
        tokenPost.addHeader("content-type", "form-data");
        tokenPost.setOption("parameters" , "?" + refreshToken.getString());
        String tokenPost_return = String(tokenPost.post("https://www.googleapis.com/oauth2/v4/token"));

        XMLNode x3     = parseJSON(tokenPost_return);
        access_token   = x3.getValueFromPath("access_token");

        SearchEngine NewToken;
        NewToken.addCriteria("UserPreference.prefkey", "Equals", "DialogFlow_access_token");
        NewToken.addData("UserPreference.prefvalue", access_token);
        NewToken.update(); //Updating the access_token value stored in database.

        return access_token; // Returning the new updated token.
      }
    }

    //POST to DialogFlow to query the user input.
    String getResponse(){
      JSONBuilder chatSend;
      chatSend.pushObject("");
      chatSend.pushObject("query_input");
      chatSend.pushObject("text");
      chatSend.addString("text", customerText.utf8Encode());
      chatSend.addString("language_code","en");
      chatSend.finalize();

      HTTP sendChatMsg;
      sendChatMsg.addHeader("content-type",  "application/json");
      sendChatMsg.addHeader("Authorization", "Bearer " + validate_token(access_token)); //Sending current access token.
      sendChatMsg.setOption("parameters" , "?" + chatSend.getString());
      String sendChatMsg_return = String(sendChatMsg.post('https://dialogflow.googleapis.com/v2/projects/'+ project_id +'/agent/sessions/'+ chatSessionId +':detectIntent'));

      return sendChatMsg_return;
    }

    //Saving the returned values needed.
    XMLNode x2             = parseJSON(getResponse());
    String response        = x2.getValueFromPath("1.fulfillmentMessages.0.text.text.0"); //Returned the first text response configured in DialogFlow.
    String confirmMsg      = x2.getValueFromPath("1.fulfillmentMessages.1.text.text.0"); //Second payload text response, Will be sent as second response.
    String intentName      = x2.getValueFromPath("1.intent.displayName");  //Returned intent name found in DialogFlow. WIll be used to decide action based on intent.
    String optionButtons   = x2.getValueFromPath("1.fulfillmentMessages.1.payload.options"); //If there are buttons configured for the first response configured in DialogFlow.
    String confirmButtons  = x2.getValueFromPath("1.fulfillmentMessages.2.payload.options"); //If there are buttons configured for the second response configured in DialogFlow.

  //DateTimes controlling when to post a message.
  DateTime msgDelay;

  //Determines next action, based on returned values from DialogFlow.
    if(intentName.toUpper().beginsWith(handOverIntent.toUpper())){//If the returned intent name is a handover intent - handover to agent(chat/ticket).
      addChatMessage(chatSessionId.toInteger(),handOverMsg ,1,botName,0,"");
      resetChat(chatSessionId.toInteger());
    }
    else if(intentName.toUpper().beginsWith(doneConversationIntent.toUpper())){//If a doneconver_ intent is recieved, close the session.
      if(response != ""){ //If the response is set in DialogFlow - send that one.
        addChatMessage(chatSessionId.toInteger(),response.utf8Decode(),1,botName,0,"");
        setChatStatus(chatSessionId.toInteger(), 7);
      }
      else{//If no text response is set in DialogFlow, send the pre-defined one below.
        addChatMessage(chatSessionId.toInteger(),goodBye,1,botName,0,"");
        setChatStatus(chatSessionId.toInteger(), 7);
      }
    }
    else if(optionButtons.getLength() > 0){//If the response has a custom payload, populate the text response with buttons.
      addChatMessage(chatSessionId.toInteger(), response.utf8Decode(), 1, botName, 17, optionButtons.utf8Decode(), msgDelay.addSec(messageDelay));
    }
    else if(confirmMsg !=""){ // If it has a second text payload, send the first one, and then the second one.
      addChatMessage(chatSessionId.toInteger(),response.utf8Decode(),1,botName,16,"showAt="+msgDelay.addSec(messageDelay).toString());
      addChatMessage(chatSessionId.toInteger(),confirmMsg.utf8Decode(),1,botName,17,confirmButtons.utf8Decode(),msgDelay.addSec(secondMsgDelay));
    }
    else{
      addChatMessage(chatSessionId.toInteger(),response.utf8Decode(),1,botName,16,"showAt="+ msgDelay.addSec(messageDelay).toString());
    }
  }
}