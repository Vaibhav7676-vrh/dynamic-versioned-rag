"use client";

import { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Chat = {
  id: string;
  title: string;
  messages: Message[];
};

export default function Home() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeChat = chats.find((c) => c.id === activeChatId);

  /* ---------------------------- */
  useEffect(() => {
    const stored = localStorage.getItem("dynamic_rag_chats");

    if (stored) {
      const parsed = JSON.parse(stored);
      setChats(parsed);
      if (parsed.length > 0) setActiveChatId(parsed[0].id);
    } else {
      createNewChat();
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("dynamic_rag_chats", JSON.stringify(chats));
  }, [chats]);

  /* ---------------------------- */
  const createNewChat = () => {
    const newChat: Chat = {
      id: uuidv4(),
      title: "New Chat",
      messages: [],
    };

    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  /* ---------------------------- */
  const deleteChat = (id: string) => {
    const updated = chats.filter((chat) => chat.id !== id);

    setChats(updated);

    if (updated.length > 0) {
      setActiveChatId(updated[0].id);
    } else {
      createNewChat();
    }
  };

  /* ---------------------------- */
  const sendMessage = async () => {
    if (!input.trim() || !activeChatId) return;

    const question = input;
    setInput("");
    setLoading(true);

    const words = question.split(" ");
    const shortTitle =
      words.length > 5
        ? words.slice(0, 5).join(" ") + "..."
        : question;

    setChats((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId
          ? {
              ...chat,
              title:
                chat.messages.length === 0
                  ? shortTitle
                  : chat.title,
              messages: [
                ...chat.messages,
                { role: "user", content: question },
                { role: "assistant", content: "" },
              ],
            }
          : chat
      )
    );

    try {
      const response = await fetch(
        "https://retrievai.onrender.com/query-stream",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question,
            k: 5,
            file_name: selectedFile?.name || null,
          }),
        }
      );

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        for (let char of chunk) {
          assistantText += char;

          await new Promise((res) => {
            setTimeout(() => {
              setChats((prev) =>
                prev.map((chat) =>
                  chat.id === activeChatId
                    ? {
                        ...chat,
                        messages: [
                          ...chat.messages.slice(0, -1),
                          { role: "assistant", content: assistantText },
                        ],
                      }
                    : chat
                )
              );
              res(null);
            }, 8);
          });
        }
      }
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  /* ---------------------------- */
  const uploadFile = async (file: File | undefined) => {
    if (!file) return;

    setSelectedFile(file);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        "https://retrievai.onrender.com/ingest-file",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) throw new Error("Upload failed");

      console.log("File uploaded successfully");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  const getFileIcon = (name: string) => {
    const ext = name.split(".").pop()?.toLowerCase();

    if (["png", "jpg", "jpeg"].includes(ext || "")) return "🖼️";
    if (["pdf"].includes(ext || "")) return "📄";
    if (["csv", "xls"].includes(ext || "")) return "📊";
    if (["txt"].includes(ext || "")) return "📄";

    return "📁";
  };

  return (
    <div className="flex h-screen bg-[#0f0f0f] text-white">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-72 bg-black border-r border-zinc-800 flex flex-col">
          <div className="p-4 font-semibold border-b border-zinc-800 flex justify-between">
            Dynamic RAG
            <button onClick={() => setSidebarOpen(false)}>✕</button>
          </div>

          <button
            onClick={createNewChat}
            className="m-4 p-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition"
          >
            + New Chat
          </button>

          <div className="flex-1 overflow-y-auto px-2 mt-4 space-y-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`flex items-center justify-between p-2 rounded-md cursor-pointer ${
                  activeChatId === chat.id
                    ? "bg-zinc-800"
                    : "bg-zinc-900 hover:bg-zinc-800"
                }`}
              >
                <span
                  onClick={() => setActiveChatId(chat.id)}
                  className="truncate flex-1"
                >
                  {chat.title}
                </span>

                <button
                  onClick={() => deleteChat(chat.id)}
                  className="text-red-400 hover:text-red-600 ml-2"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto px-8 py-10 max-w-4xl mx-auto w-full space-y-10">
          {activeChat?.messages.map((msg, i) => (
            <div key={i}>
              {msg.role === "user" && (
                <div className="flex justify-end">
                  <div className="bg-blue-600 px-5 py-3 rounded-2xl max-w-xl">
                    {msg.content}
                  </div>
                </div>
              )}

              {msg.role === "assistant" && (
                <div className="flex items-start gap-3">
                  <div className="mt-2 w-2 h-2 rounded-full bg-zinc-400"></div>
                  <div className="text-zinc-200 whitespace-pre-wrap">
                    {msg.content}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* INPUT */}
        <div className="p-6 border-t border-zinc-800">
          <div className="max-w-3xl mx-auto flex gap-3 items-center">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask anything..."
              className="flex-1 bg-zinc-900 rounded-xl px-4 py-3"
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              className="bg-blue-600 px-6 rounded-xl"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}