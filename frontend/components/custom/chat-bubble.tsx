"use client";

import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ToolInvocation } from "ai";
import { Message } from "ai/react";
import Riddle from "./riddle";

export default function ChatBubble({
  message: m,
  addToolResult,
}: {
  message?: Message;
  addToolResult: Function;
}) {
  if (m?.role === "system") return null;
  const isUser = m?.role === "user";
  return (
    <div
      className={`whitespace-pre-wrap max-w-fit w-full flex gap-0 items-start m-1 ${
        isUser ? "self-end flex-row-reverse" : "flex-row"
      }`}
    >
      <Avatar className='shadow-md'>
        <AvatarImage
          src={
            isUser
              ? "https://images.unsplash.com/photo-1445053023192-8d45cb66099d?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
              : "https://github.com/shadcn.png"
          }
          className='contain'
        />
        <AvatarFallback>{isUser ? "U" : "AI"}</AvatarFallback>
      </Avatar>

      <div
        className={`rounded-md mx-1 px-2 py-1 text-stone-900 shadow-md ${
          isUser
            ? "bg-stone-200 border border-stone-300 ml-10"
            : "bg-blue-100 border border-blue-200 self-end mr-10"
        }`}
      >
        {m?.content?.trim()}
        {m?.toolInvocations?.map((toolInvocation: ToolInvocation) => {
          const toolCallId = toolInvocation.toolCallId;
          const addResult = (result: string) =>
            addToolResult({ toolCallId, result });

          // render confirmation tool (client-side tool with user interaction)
          if (toolInvocation.toolName === "riddle") {
            // @ts-ignore
            const content = toolInvocation?.result?.content;
            return (
              <Riddle
                key={toolCallId}
                content={content}
                addResult={addResult}
                toolInvocation={toolInvocation}
              />
            );
          }
          // other tools:
          return "result" in toolInvocation ? (
            <div key={toolCallId}>
              Tool call {`${toolInvocation.toolName}: `}
              {toolInvocation.result}
            </div>
          ) : (
            <div key={toolCallId}>Calling {toolInvocation.toolName}...</div>
          );
        })}
      </div>
    </div>
  );
}
