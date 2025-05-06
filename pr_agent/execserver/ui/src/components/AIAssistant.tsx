import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your PR-Agent assistant. How can I help you today?',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    // Simulate AI response after a delay
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `I received your message: "${input}". This is a placeholder response as the AI assistant functionality is still being implemented.`,
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="card">
      <div className="card-header">AI Assistant</div>
      <div className="card-body">
        <div className="chat-container" style={{ height: '400px', overflowY: 'auto' }}>
          {messages.map(message => (
            <div 
              key={message.id} 
              className={`chat-message ${message.sender === 'ai' ? 'ai' : 'user'}`}
              style={{
                marginBottom: '10px',
                padding: '10px',
                borderRadius: '5px',
                backgroundColor: message.sender === 'ai' ? 'var(--chat-ai-bg)' : 'var(--chat-user-bg)',
                textAlign: message.sender === 'user' ? 'right' : 'left'
              }}
            >
              <div className="message-content">{message.text}</div>
              <div 
                className="message-timestamp" 
                style={{ 
                  fontSize: '0.8rem', 
                  color: 'var(--secondary-color)',
                  marginTop: '5px'
                }}
              >
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="mt-3">
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Type your message here..."
              value={input}
              onChange={handleInputChange}
              disabled={loading}
            />
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading || !input.trim()}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AIAssistant;

