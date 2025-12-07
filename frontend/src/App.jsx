import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your Weather Bot. Ask me about the temperature in any city.", sender: "bot" }
  ])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputText.trim()) return

    const userMessage = { text: inputText, sender: "user" }
    setMessages(prev => [...prev, userMessage])
    setInputText("")
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.text })
      })

      const data = await response.json()
      const botMessage = { text: data.response, sender: "bot" }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      setMessages(prev => [...prev, { text: "Sorry, I'm having trouble connecting to the server.", sender: "bot" }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend()
    }
  }

  return (
    <>
      <h1>Weather Chatbot</h1>
      <div className="chat-container">
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && <div className="message bot-message">Typing...</div>}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a city name..."
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading}>
            Send
          </button>
        </div>
      </div>
    </>
  )
}

export default App
