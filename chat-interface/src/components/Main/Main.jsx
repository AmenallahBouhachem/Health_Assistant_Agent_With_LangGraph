import{ useState, useRef, useEffect } from "react";
import "./Main.css";
import { marked } from "marked"; 
import { assets } from "../../assets/assets";

const apiUrl = "http://localhost:8001";

const Main = ({ messages, setMessages, showGreeting, setShowGreeting}) => {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  // Extract the last 4 messages (excluding the current one) for context
  const getConversationHistory = () => {
    if (messages.length <= 1) return [];
  
    return messages
      .slice(Math.max(messages.length - 4, 0), messages.length - 1)
      .map(msg => ({
        type: msg.type,
        text: msg.text
      }));
  };
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
 
  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    setIsTyping(true);
    try {
      const userMessage = { type: "user", text: input };
      setMessages((prev) => [...prev, userMessage]);
      const currentInput = input;
      setInput("");
      setShowGreeting(false);
      setTimeout(scrollToBottom, 100);
      const convHistory = getConversationHistory();

      const response = await fetch(`${apiUrl}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({  
          task: currentInput,
          conv: convHistory,
          
        }),
      });

      if (!response.ok) throw new Error("API request failed");
      
      const { response: fullResponse } = await response.json();
      
      setIsTyping(false);
      setIsStreaming(true);

      setMessages((prev) => [...prev, { type: "bot", text: "", isStreaming: true }]);

      let streamedText = '';
      for (let char of fullResponse) {
        streamedText += char;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.type === "bot" && msg.isStreaming
              ? { ...msg, text: streamedText }
              : msg
          )
        );
        scrollToBottom();
        await new Promise((resolve) => setTimeout(resolve, 3));
      }
  
      setMessages((prev) =>
        prev.map((msg) =>
          msg.type === "bot" && msg.isStreaming
            ? { ...msg, text: fullResponse, isStreaming: false }
            : msg
        )
      );
      scrollToBottom();
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "Sorry, there was an error processing your question.", error: true }
      ]);
      scrollToBottom();
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  return (
    <div className="main">
      <div className="nav">
        <p>Healthcare Assistant</p>
      </div>
      <div className="main-container">
        {showGreeting && (
          <div className="greet">
            <p className="text-sm mb-5">
              <span>Hello, I am your Healthcare Assistant.</span>
            </p>
            <p className="text-sm">How can I help you today?</p>
          </div>
        )}

        <div className="messages">
          {messages.map((message, index) =>
            message.type === "user" ? (
              <div key={index} className="message user">
                <div className="message-bubble user">
                  <p>{message.text}</p>
                </div>
              </div>
            ) : (
              <div key={index} className="message bot">
                <div className="message-bubble bot">
                  <div className="bot-response">
                    {(message.text || message.isStreaming) && (
                      <img src={assets.chat_logo} alt="Bot Icon" className="bot-icon" />
                    )}
                    <div
                      dangerouslySetInnerHTML={{ __html: marked(message.text) }}
                    ></div>
                  </div>
                </div>
              </div>
            )
          )}
          {isTyping && (
            <div className="message bot">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="main-bottom">
          <div className="search-box">
            <input
              type="text"
              placeholder="Enter a prompt here"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isLoading) {
                  e.preventDefault(); 
                  handleSendMessage();
                }
              }}
              className={isLoading ? "input-disabled" : ""}
            />
            <div>
              {isLoading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                </div>
              ) : (
                <img
                  src={assets.send_icon}
                  alt="send"
                  onClick={handleSendMessage}
                  className={!input.trim() ? "send-disabled" : ""}
                />
              )}
            </div>
          </div>
          <p className="bottom-info"></p>
        </div>
      </div>
    </div>
  );
};

export default Main;
