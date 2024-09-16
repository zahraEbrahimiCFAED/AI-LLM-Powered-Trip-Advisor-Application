"use client";

import React from "react";
import RiddleDialog from "./RiddleDialog";
import { ToolInvocation } from "ai";
import { Button } from "../ui/button";

export default function Riddle({
  content,
  addResult,
  toolInvocation,
}: {
  content: any;
  addResult: Function;
  toolInvocation: ToolInvocation;
}) {
  const [answer, setAnswer] = React.useState<string | null>(null);
  function transformToJSObject(inputString: string) {
    try {
      // Replace single quotes with double quotes
      const jsonString = inputString.replace(/'/g, '"');

      // Parse the string into a JavaScript array
      const jsObject = JSON.parse(jsonString);

      return jsObject ?? [];
    } catch (error) {
      return [];
    }
  }
  console.log(
    "%cfrontend/components/custom/riddle.tsx:17 content",
    "color: #007acc;",
    content
  );
  const allAnswers = transformToJSObject(content?.false_answers);
  allAnswers.push(content?.answer);
  allAnswers.sort(() => Math.random() - 0.5);

  console.log(
    "%cfrontend/components/custom/riddle.tsx:26 allAnswers",
    "color: #007acc;",
    allAnswers
  );

  const getText = () => {
    const a = content?.answer;
    if (answer === a) {
      return `Correct! The answer is ${answer}! ${content?.explanation}`;
    } else {
      return `Wrong! The correct answer is ${answer}. Let's do another one!`;
    }
  };
  return (
    <div className='flex flex-col p-2 gap-2'>
      <p className='text-base'>{content?.riddle}</p>
      <div className='flex flex-wrap gap-2 justify-start max-w-screen-sm'>
        {answer === content?.answer ? (
          <p className=''>{getText()}</p>
        ) : (
          allAnswers.map((answer: string) => (
            <Button
              variant='secondary'
              key={answer}
              onClick={() => setAnswer(answer)}
            >
              {answer}
            </Button>
          ))
        )}
      </div>
      <p className='italic text-sm'>
        Write the answer in the chat or click below for more information.
      </p>
      <RiddleDialog {...content} />
    </div>
  );
}
