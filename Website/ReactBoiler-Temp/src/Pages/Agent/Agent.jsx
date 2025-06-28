"use client";

import React, { useState, useEffect, useRef } from "react";
import { Button, Avatar, Card, CardBody, Textarea } from "@nextui-org/react";
import { Bot, Send, PlusCircle, User, Upload, FileText, X } from "lucide-react";
import ReactMarkdown from "react-markdown"; // Import react-markdown

// Sub-component for chat content with manual state management
function ChatContent({ onTitleChange }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if ((input.trim() || uploadedFile) && !isLoading) {
        onSubmit(e);
      }
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file type
      const validTypes = ['.yaml', '.yml', '.json'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!validTypes.includes(fileExtension)) {
        alert('Please upload only YAML (.yaml, .yml) or JSON (.json) files');
        return;
      }

      setUploadedFile(file);
      
      // Read file content
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileContent(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setFileContent("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() && !uploadedFile) return;

    // Prepare message content for display
    let messageContent = input.trim();
    if (uploadedFile) {
      messageContent = `${messageContent}\n\n**Uploaded File: ${uploadedFile.name}**\n\`\`\`${uploadedFile.name.endsWith('.json') ? 'json' : 'yaml'}\n${fileContent}\n\`\`\``;
    }

    // Add user's message to the chat
    const userMessage = { role: "user", content: messageContent };
    setMessages((prev) => [...prev, userMessage]);

    // Update title on the first message
    if (messages.length === 0) {
      const titleText = uploadedFile ? `Analysis: ${uploadedFile.name}` : (input.trim() || "Configuration Analysis");
      onTitleChange(titleText.length > 30 ? titleText.substring(0, 30) + "..." : titleText);
    }

    setIsLoading(true);

    // Store current input/file state before clearing
    const currentInput = input.trim();
    const currentFile = uploadedFile;
    const currentFileContent = fileContent;

    try {
      // Step 1: Use intelligent filtration to determine which function to call
      const filterResponse = await fetch("http://localhost:5001/api/filter-request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          has_file: !!currentFile,
          file_type: currentFile ? currentFile.type : ''
        }),
      });

      if (!filterResponse.ok) {
        throw new Error("Failed to classify request");
      }

      const classification = await filterResponse.json();
      
      // Extract the actual classification from the nested structure
      const classificationData = classification.classification || classification;
      
      // Log classification for debugging
      console.log("Request classified as:", classificationData);

      // Step 2: Execute the appropriate function
      const executeResponse = await fetch("http://localhost:5001/api/execute-function", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          function: classificationData.function,
          params: classificationData.extracted_params || {},
          message: currentInput,
          file_content: currentFileContent
        }),
      });

      const data = await executeResponse.json();

      if (executeResponse.ok) {
        let content = data.response?.value || data.message || 'Response received';
        
        // Add function type indicator with emoji
        const functionEmojis = {
          'chat': '💬',
          'config-analysis': '🔍', 
          'repo-analysis': '📊',
          'create-issue': '🎫',
          'list-issues': '📋'
        };
        
        const emoji = functionEmojis[classificationData.function] || '🤖';
        content = `${emoji} ${content}`;
        
        // Process annotations if they exist
        const annotations = data.response?.annotations || [];
        annotations.forEach((annotation, index) => {
          const marker = annotation.text;
          const footnoteNumber = index + 1;
          const footnoteText = ``;
          content = content.replace(marker, footnoteText);
        });

        // Append references section if annotations exist
        if (annotations.length > 0) {
          content += "\n\n---\n\n**References:**\n";
          annotations.forEach((annotation, index) => {
            const footnoteNumber = index + 1;
            content += `${footnoteNumber}. ${annotation.file_citation?.file_id || 'Reference'}\n`;
          });
        }

        const assistantMessage = { 
          role: "assistant", 
          content,
          classification: {
            function: classificationData.function,
            confidence: classificationData.confidence,
            emoji: emoji
          }
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
        { role: "assistant", content: "❌ Sorry, unable to connect to the server. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
      setInput("");
      // Clear uploaded file after sending
      removeFile();
    }
  };

  return (
    <>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-gray-100 border-2 border-gray-200 rounded-full flex items-center justify-center mb-4">
              <Bot size={32} className="text-black" />
            </div>
            <h2 className="text-2xl font-bold text-black mb-2">
              Welcome to ACI.dev SRE Agent
            </h2>
            <p className="text-gray-600 max-w-md mb-6">
              Your intelligent SRE assistant powered by ACI.dev! Upload configs, analyze repos, create GitHub issues, or chat about SRE best practices.
            </p>
            <div className="flex flex-col items-center gap-4">
              <Button
                onClick={triggerFileUpload}
                className="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg"
                startContent={<Upload size={18} />}
              >
                Upload Configuration File
              </Button>
              <p className="text-sm text-gray-500">
                💬 Chat • 🔍 Config Analysis • 📊 Repo Analysis • 🎫 GitHub Issues
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((message, i) => (
              <div
                key={i}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex items-start gap-3 max-w-[80%] ${
                    message.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  <Avatar
                    icon={
                      message.role === "user" ? (
                        <User size={18} />
                      ) : (
                        <Bot size={18} />
                      )
                    }
                    className={
                      message.role === "user"
                        ? "bg-black text-white"
                        : "bg-gray-100 border border-gray-200 text-black"
                    }
                  />
                  <Card
                    className={`shadow-md rounded-lg border ${
                      message.role === "user" 
                        ? "bg-black text-white border-black" 
                        : "bg-white border-gray-200"
                    }`}
                  >
                    <CardBody className="p-4">
                      {message.role === "assistant" ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        <p>{message.content}</p>
                      )}
                    </CardBody>
                  </Card>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-3">
                  <Avatar
                    icon={<Bot size={18} />}
                    className="bg-gray-100 border border-gray-200 text-black"
                  />
                  <Card className="bg-white shadow-md rounded-lg border border-gray-200">
                    <CardBody className="p-4">
                      <div className="flex gap-1">
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        />
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        />
                      </div>
                    </CardBody>
                  </Card>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="w-full max-w-3xl mx-auto px-4">
        {/* File Upload Input (Hidden) */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".yaml,.yml,.json"
          className="hidden"
        />
        
        {/* Uploaded File Display */}
        {uploadedFile && (
          <Card className="mb-3 border border-gray-200 bg-gray-50">
            <CardBody className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-black" />
                  <span className="text-sm font-medium text-black">{uploadedFile.name}</span>
                  <span className="text-xs text-gray-500">({(uploadedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <Button
                  isIconOnly
                  size="sm"
                  variant="light"
                  onClick={removeFile}
                  className="text-gray-500 hover:text-red-500"
                >
                  <X size={14} />
                </Button>
              </div>
            </CardBody>
          </Card>
        )}

        <Card className="border-2 border-gray-200 shadow-sm bg-white rounded-2xl hover:border-black transition-colors">
          <form onSubmit={onSubmit} className="relative">
            <Textarea
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={uploadedFile ? "Add context or questions about your configuration..." : "Ask about SRE practices, upload configs, analyze repos (owner/repo), or create GitHub issues..."}
              className="min-h-[40px] max-h-[50px] py-2 px-4 pr-20 resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-2xl"
            />
            <div className="absolute right-2 bottom-2 flex gap-1">
              <Button
                type="button"
                isIconOnly
                onClick={triggerFileUpload}
                className="h-8 w-8 rounded-full text-gray-500 bg-transparent hover:bg-gray-100 hover:text-black transition-colors"
              >
                <Upload size={16} />
              </Button>
              <Button
                type="submit"
                isIconOnly
                className={`h-8 w-8 rounded-full ${
                  (!input.trim() && !uploadedFile) || isLoading
                    ? "text-gray-400 bg-transparent hover:bg-transparent"
                    : "bg-black hover:bg-gray-800 text-white"
                }`}
                disabled={(!input.trim() && !uploadedFile) || isLoading}
              >
                <Send size={16} />
              </Button>
            </div>
          </form>
        </Card>
        <p className="text-xs text-center text-gray-500 mt-2">
          SRE Guardian can make mistakes. Consider verifying important configuration details.
        </p>
      </div>
    </>
  );
}

export default function ChatInterface() {
  const [chatKey, setChatKey] = useState(0);
  const [chatTitle, setChatTitle] = useState("New Analysis");

  const startNewChat = () => {
    setChatKey((prev) => prev + 1); // Remount ChatContent to reset chat
    setChatTitle("New Analysis");
  };

  const handleTitleChange = (newTitle) => {
    setChatTitle(newTitle);
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <Card className="rounded-none shadow-sm border-b border-gray-200">
        <CardBody className="py-4 px-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-black">{chatTitle}</h1>
            <Button
              onPress={startNewChat}
              className="bg-black hover:bg-gray-800 text-white rounded-lg px-6 py-3"
              startContent={<PlusCircle size={18} />}
            >
              New Analysis
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Chat content with key to force remount */}
      <ChatContent key={chatKey} onTitleChange={handleTitleChange} />
    </div>
  );
}