"use client";

import { Message, useChat } from "ai/react";
import ChatBubble from "@/components/custom/chat-bubble";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const placeholders = [
  "What is the biggest island of MV?",
  "What is the capital of MV?",
  "What is the population of MV?",
  "Which league plays the football club Hansa Rostock?",
  "What is the name of the biggest lake in MV?",
];

const initialMessages: Message[] = [
  {
    role: "system",
    id: "1",
    content: `You represent the state of MV, Germany. The users will follow a paper chase around the region, where a riddle will be prompted for each point of interest. Solving the riddle will result in the next point of interest. Don't give the solution to the riddle! Don't mention that it is a paper chase. Instead, call it exploration. Provide all the information the user needs to solve the riddle and motivate them to explore the region and solve all the riddles. Never provide markdown - only simple text.`,
  },
  {
    role: "assistant",
    id: "2",
    content: `Moin Lydia, nice to meet you! I'm excited to show you around MV. Are you ready to solve some riddles and explore the region?`,
  },
];

export default function Chat() {
  const {
    messages,
    handleInputChange,
    handleSubmit,
    setInput,
    input,
    isLoading,
    addToolResult,
  } = useChat({
    maxToolRoundtrips: 5,
    keepLastMessageOnError: true,
    initialMessages,
    experimental_prepareRequestBody: (options) => {
      const setupString = localStorage.getItem("setup");
      const setup = JSON.parse(setupString || "{}");
      return JSON.stringify({
        messages: options.messages,
        setup,
      });
    },
  });

  const filteredMessages = messages.filter((msg, index, array) => {
    // Include the first message or if the previous message is not from the assistant
    return (
      index === 0 ||
      !(msg.role === "assistant" && array[index - 1].role === "assistant")
    );
  });

  return (
    <div className='max-w-sm'>
      <div className='flex flex-col gap-3 w-full max-w-md mx-auto stretch mt-4 mb-28'>
        {filteredMessages.map((m) => (
          <ChatBubble key={m.id} message={m} addToolResult={addToolResult} />
        ))}

        {isLoading && (
          <div className='flex flex-row items-start'>
            <Avatar className='shadow-md'>
              <AvatarImage
                src='https://github.com/shadcn.png'
                className='contain'
              />
              <AvatarFallback>"AI"</AvatarFallback>
            </Avatar>
            <div className='bg-blue-100 border border-blue-200 self-end mr-10 rounded-md mx-1 px-2 py-1 text-stone-900 shadow-md animate-pulse'>
              Typing...
            </div>
          </div>
        )}

        <div className='flex flex-row gap-2 fixed bottom-16 mb-1 w-full justify-center'>
          <Button
            className='shadow-xl border border-stone-600 rounded-full'
            variant='secondary'
            onClick={() => setInput("Give me a hint.")}
          >
            Give me a hint
          </Button>
          <Button
            className='shadow-xl rounded-full border border-stone-600'
            variant='secondary'
            onClick={() => setInput("Give me a new riddle.")}
          >
            Give me a new riddle
          </Button>
        </div>

        <PlaceholdersAndVanishInput
          placeholders={placeholders}
          onChange={handleInputChange}
          onSubmit={handleSubmit}
          input={input}
        />
      </div>
      <div className='fixed bottom-0 w-full dark:from-black light:from-white z-10 h-16 bg-gradient-to-t to-transparent to-95% from-75%' />
    </div>
  );
}
