import  { useState } from 'react';
import Sidebar from './components/Sidebar/Sidebar';
import Main from './components/Main/Main';


const App = () => {
  const [messages, setMessages] = useState([]);
  const [showGreeting, setShowGreeting] = useState(true);
  

 

  const handleNewChat = () => {
    // Simply reset the state without creating a new chat
    setMessages([]);
    setShowGreeting(true);
  };

  return (
    <>
      <Sidebar 
        onNewChat={handleNewChat} 
        setMessages={setMessages}
        setShowGreeting={setShowGreeting}
        
      />
      <Main
        messages={messages}
        setMessages={setMessages}
        showGreeting={showGreeting}
        setShowGreeting={setShowGreeting}
       
      />
    </>
  );
};

export default App;