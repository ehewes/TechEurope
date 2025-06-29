"use client"

import React from "react"
import { useState, useEffect, useRef } from "react"
import { Button, Textarea, Avatar, Badge } from "@nextui-org/react"
import { Bot, Send, Plus, User, Upload, FileText, X, Paperclip } from "lucide-react"

// Markdown renderer component
function MarkdownRenderer({ content }) {
  const parseMarkdown = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
      .replace(
        /```(\w+)?\n([\s\S]*?)```/g,
        '<pre class="bg-gray-900 text-gray-100 p-4 rounded-md overflow-x-auto my-3 font-mono text-sm"><code>$2</code></pre>',
      )
      .replace(/\n/g, "<br>")
  }

  return <div className="prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }} />
}

// File upload component
function FileUpload({
  onFileSelect,
  uploadedFile,
  onRemoveFile,
}) {
  const fileInputRef = useRef(null)

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const validTypes = [".yaml", ".yml", ".json"]
      const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()

      if (!validTypes.includes(fileExtension)) {
        alert("Please upload only YAML (.yaml, .yml) or JSON (.json) files")
        return
      }

      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result
        onFileSelect(file, content)
      }
      reader.readAsText(file)
    }
  }

  const triggerFileUpload = () => {
    fileInputRef.current?.click()
  }

  return (
    <>
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept=".yaml,.yml,.json" className="hidden" />

      {uploadedFile && (
        <div className="mb-3 p-3 border border-gray-200 rounded-lg bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText size={16} className="text-gray-600" />
              <span className="text-sm font-medium text-gray-900">{uploadedFile.name}</span>
              <Badge color="default" size="sm" className="text-xs">
                {(uploadedFile.size / 1024).toFixed(1)} KB
              </Badge>
            </div>
            <Button
              size="sm"
              variant="light"
              onClick={onRemoveFile}
              className="h-6 w-6 min-w-6 p-0 text-gray-400 hover:text-gray-600"
            >
              <X size={14} />
            </Button>
          </div>
        </div>
      )}

      <Button
        type="button"
        size="sm"
        variant="ghost"
        onClick={triggerFileUpload}
        className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600 hover:bg-gray-100"
      >
        <Paperclip size={16} />
      </Button>
    </>
  )
}

// Typing indicator component
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start gap-3 max-w-[80%]">
        <Avatar
          icon={<Bot size={16} />}
          className="h-8 w-8 bg-black text-white"
        />
        <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Message component
function Message({ message, isUser }) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`flex items-start gap-3 max-w-[85%] ${isUser ? "flex-row-reverse" : ""}`}>
        <Avatar
          icon={isUser ? <User size={16} /> : <Bot size={16} />}
          className={`h-8 w-8 ${isUser ? "bg-gray-900" : "bg-black"} text-white`}
        />
        <div
          className={`rounded-lg border shadow-sm ${
            isUser ? "bg-black text-white border-black" : "bg-white border-gray-200"
          }`}
        >
          <div className="p-4">
            {isUser ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
            ) : (
              <div className="text-sm leading-relaxed">
                <MarkdownRenderer content={message.content} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Welcome screen component
function WelcomeScreen({ onFileUpload }) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 bg-black rounded-lg flex items-center justify-center mb-8">
        <Bot size={32} className="text-white" />
      </div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-4">SRE Configuration Assistant</h2>
      <p className="text-gray-600 max-w-lg mb-8 leading-relaxed">
        Analyze configuration files, review infrastructure setups, and get recommendations for SRE best practices.
      </p>
      <Button
        onClick={onFileUpload}
        className="bg-black hover:bg-gray-800 text-white px-6 py-2.5 rounded-md transition-colors"
      >
        <Upload size={16} className="mr-2" />
        Upload Configuration
      </Button>
      <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm text-gray-500">
        <span className="px-3 py-1 bg-gray-100 rounded-full">Configuration Analysis</span>
        <span className="px-3 py-1 bg-gray-100 rounded-full">Best Practices</span>
        <span className="px-3 py-1 bg-gray-100 rounded-full">Infrastructure Review</span>
      </div>
    </div>
  )
}

// Main chat content component
function ChatContent({ onTitleChange }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [fileContent, setFileContent] = useState("")
  const messagesEndRef = useRef(null)
  const fileUploadRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  const handleFileSelect = (file, content) => {
    setUploadedFile(file)
    setFileContent(content)
  }

  const removeFile = () => {
    setUploadedFile(null)
    setFileContent("")
  }

  const triggerFileUpload = () => {
    fileUploadRef.current?.click()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() && !uploadedFile) return

    let messageContent = input.trim()
    if (uploadedFile) {
      messageContent = `${messageContent}\n\n**File: ${uploadedFile.name}**\n\`\`\`${uploadedFile.name.endsWith(".json") ? "json" : "yaml"}\n${fileContent}\n\`\`\``
    }

    const userMessage = { role: "user", content: messageContent }
    setMessages((prev) => [...prev, userMessage])

    if (messages.length === 0) {
      const titleText = uploadedFile ? `${uploadedFile.name}` : input.trim() || "Configuration Analysis"
      onTitleChange(titleText.length > 40 ? titleText.substring(0, 40) + "..." : titleText)
    }

    setIsLoading(true)
    setInput("")
    removeFile()

    try {
      // Call the real Flask API endpoint
      const requestBody = {
        message: input.trim()
      };
      
      // Add file content if a file was uploaded
      if (uploadedFile && fileContent) {
        requestBody.file_content = fileContent;
      }

      const response = await fetch("http://localhost:5001/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (response.ok) {
        const content = data.response?.value || data.message || 'Response received';
        const assistantMessage = { 
          role: "assistant", 
          content: content
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage = { 
          role: "assistant", 
          content: `❌ Error: ${data.error || 'Something went wrong'}` 
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "❌ Sorry, unable to connect to the server. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if ((input.trim() || uploadedFile) && !isLoading) {
        handleSubmit(e)
      }
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        {messages.length === 0 ? (
          <WelcomeScreen onFileUpload={triggerFileUpload} />
        ) : (
          <div className="max-w-4xl mx-auto">
            {messages.map((message, i) => (
              <Message key={i} message={message} isUser={message.role === "user"} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-4xl mx-auto">
          {/* File Upload Display */}
          {uploadedFile && (
            <div className="mb-4 p-3 border border-gray-200 rounded-lg bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-gray-600" />
                  <span className="text-sm font-medium text-gray-900">{uploadedFile.name}</span>
                  <Badge color="default" size="sm">
                    {(uploadedFile.size / 1024).toFixed(1)} KB
                  </Badge>
                </div>
                <Button
                  size="sm"
                  variant="light"
                  isIconOnly
                  onClick={removeFile}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={14} />
                </Button>
              </div>
            </div>
          )}

          {/* Chat Input */}
          <form onSubmit={handleSubmit} className="flex items-end gap-3">
            <div className="flex-1">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  uploadedFile
                    ? "Ask questions about your configuration..."
                    : "Describe your infrastructure setup or ask about SRE best practices..."
                }
                minRows={1}
                maxRows={6}
                variant="bordered"
                className="w-full"
                classNames={{
                  input: "text-sm",
                  inputWrapper: "border-gray-300 hover:border-gray-400 focus-within:!border-black"
                }}
              />
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-2 pb-2">
              {/* File Upload Button */}
              <input
                type="file"
                ref={fileUploadRef}
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    const validTypes = [".yaml", ".yml", ".json"]
                    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()

                    if (!validTypes.includes(fileExtension)) {
                      alert("Please upload only YAML (.yaml, .yml) or JSON (.json) files")
                      return
                    }

                    const reader = new FileReader()
                    reader.onload = (event) => {
                      handleFileSelect(file, event.target?.result)
                    }
                    reader.readAsText(file)
                  }
                }}
                accept=".yaml,.yml,.json"
                className="hidden"
              />
              <Button
                type="button"
                variant="flat"
                isIconOnly
                onClick={triggerFileUpload}
                className="bg-gray-100 hover:bg-gray-200 text-gray-600"
              >
                <Paperclip size={18} />
              </Button>
              
              {/* Send Button */}
              <Button
                type="submit"
                color="primary"
                isIconOnly
                disabled={(!input.trim() && !uploadedFile) || isLoading}
                className="bg-black hover:bg-gray-800 text-white disabled:bg-gray-200 disabled:text-gray-400"
              >
                <Send size={18} />
              </Button>
            </div>
          </form>

          <p className="text-xs text-center text-gray-500 mt-3">
            AI-generated responses may contain errors. Verify critical configurations independently.
          </p>
        </div>
      </div>
    </div>
  )
}

// Main component
export default function AgentChat() {
  const [chatKey, setChatKey] = useState(0)
  const [chatTitle, setChatTitle] = useState("New Analysis")

  const startNewChat = () => {
    setChatKey((prev) => prev + 1)
    setChatTitle("New Analysis")
  }

  const handleTitleChange = (newTitle) => {
    setChatTitle(newTitle)
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-black rounded-md flex items-center justify-center">
                <Bot size={18} className="text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">{chatTitle}</h1>
            </div>
            <Button
              onClick={startNewChat}
              variant="bordered"
              className="border-gray-300 hover:bg-gray-50 px-4 py-2 rounded-md"
            >
              <Plus size={16} className="mr-2" />
              New Analysis
            </Button>
          </div>
        </div>
      </div>

      {/* Chat Content */}
      <ChatContent key={chatKey} onTitleChange={handleTitleChange} />
    </div>
  )
}
