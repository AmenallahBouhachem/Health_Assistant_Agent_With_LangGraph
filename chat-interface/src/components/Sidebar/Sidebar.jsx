import { useState} from "react";
import "./Sidebar.css";
import { RiChatNewLine } from "react-icons/ri";
const Sidebar = ({ setMessages, setShowGreeting}) => {
  const [extended, setExtended] = useState(true);


  

  const handleNewChat = () => {
    setMessages([]); 
    setShowGreeting(true); 
  };
  
  return (
    <div className="sidebar">
      <div className="top">
        
        <div className="new-chat" onClick={handleNewChat}>
            <RiChatNewLine className="chat-icon" />
            {extended && <p>New Chat</p>}
        </div>
        
      </div>
    </div>
  );
};

export default Sidebar;
