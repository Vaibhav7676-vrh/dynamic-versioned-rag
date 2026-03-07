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
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const dropRef = useRef<HTMLDivElement>(null);

  const activeChat = chats.find((c) => c.id === activeChatId);

  /* ----------------------------
      Load Chats
  ---------------------------- */
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

  /* ----------------------------
      Load Version Files
  ---------------------------- */
  useEffect(() => {
    fetch("http://localhost:8000/versions")
      .then((res) => res.json())
      .then((data) => {
        if (data.active_version && data.versions[data.active_version]) {
          setUploadedFiles(data.versions[data.active_version]);
        }
      })
      .catch(() => {});
  }, []);

  /* ----------------------------
      Persist Chats
  ---------------------------- */
  useEffect(() => {
    localStorage.setItem("dynamic_rag_chats", JSON.stringify(chats));
  }, [chats]);

  /* ----------------------------
      Create New Chat
  ---------------------------- */
  const createNewChat = () => {
    const newChat: Chat = {
      id: uuidv4(),
      title: "New Chat",
      messages: [],
    };

    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  /* ----------------------------
     Send Message (Streaming)
  ---------------------------- */
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
      const response = await fetch("http://localhost:8000/query-stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, k: 5 }),
      });

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        assistantText += decoder.decode(value, { stream: true });

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
      }
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  /* ----------------------------
     File Upload
  ---------------------------- */
  const uploadFile = async (file: File | undefined) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/ingest-file", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      // Reload version data
      const versionRes = await fetch("http://localhost:8000/versions");
      const data = await versionRes.json();
      if (data.active_version && data.versions[data.active_version]) {
        setUploadedFiles(data.versions[data.active_version]);
      }
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  /* ----------------------------
     Drag & Drop
  ---------------------------- */
  useEffect(() => {
    const dropArea = dropRef.current;
    if (!dropArea) return;

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer?.files?.[0];
      if (file) uploadFile(file);
    };

    dropArea.addEventListener("dragover", handleDragOver);
    dropArea.addEventListener("drop", handleDrop);

    return () => {
      dropArea.removeEventListener("dragover", handleDragOver);
      dropArea.removeEventListener("drop", handleDrop);
    };
  }, []);

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

          <div
            ref={dropRef}
            className="mx-4 mb-3 p-4 border border-dashed border-zinc-700 rounded-lg text-center text-sm text-zinc-400"
          >
            Drag & Drop File Here
          </div>

          <div className="px-4 mb-4">
            <input
              type="file"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) uploadFile(file);
              }}
              className="text-sm text-zinc-400"
            />
          </div>

          <div className="px-4 text-sm text-zinc-400">
            <div className="mb-2 font-semibold text-zinc-300">
              Uploaded Files
            </div>
            <ul className="space-y-1">
              {uploadedFiles.map((file, i) => (
                <li key={i} className="truncate">
                  • {file}
                </li>
              ))}
            </ul>
          </div>

          <div className="flex-1 overflow-y-auto px-2 mt-4 space-y-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => setActiveChatId(chat.id)}
                className={`p-2 rounded-md cursor-pointer truncate transition ${
                  activeChatId === chat.id
                    ? "bg-zinc-800"
                    : "bg-zinc-900 hover:bg-zinc-800"
                }`}
              >
                {chat.title}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {!sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 bg-black border-b border-zinc-800"
          >
            ☰
          </button>
        )}

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
                  <div className="text-zinc-200 leading-7 whitespace-pre-wrap text-[15px]">
                    {msg.content}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="p-6 border-t border-zinc-800">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Message Dynamic RAG..."
              className="flex-1 bg-zinc-900 rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-zinc-700"
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              className="bg-blue-600 px-6 rounded-xl hover:bg-blue-700 transition"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}