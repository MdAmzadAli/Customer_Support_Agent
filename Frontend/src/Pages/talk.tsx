import React, { useState, useEffect, useRef } from "react"
import api from "../utils/api"

interface Chat {
  user_message: string
  bot_response: string|null
  created_at: string|null
}

interface DataResponse{
    response:any
}


export default function TalkToAgent() {
  const chat_objects = Array.from({ length: 1 }, (_, i) => ({
  user_message: `hello ${i + 1}`,
  bot_response: "how are you?",
  created_at: "now",
}))
  const [chats, setChats] = useState<Chat[]>(chat_objects)
  const [input, setInput] = useState("")
  const [isbotloading,setisbotloading]=useState(false)

  const textareaRef = useRef<HTMLTextAreaElement>(null)

// Auto resize logic
useEffect(() => {
  if (textareaRef.current) {
    textareaRef.current.style.height = "auto"       
    textareaRef.current.style.height = textareaRef.current.scrollHeight + "px"  
  }
}, [input]) 

useEffect(()=>{

const get_data=async()=>{
    try{
        const response=await api.get("/user/data");
        console.log("get_data:",response.data.response)
        const res=response.data.response;
        if(res.length){
            setChats(res);
        }
    }
    catch(e){
    console.log("Error in fetching data",e)
    }
}
get_data();  

},[])

const handleSend = async () => {
  if (!input.trim()) return
  const input_value = input.trim()

  try {
    setInput("")
    setChats(prev => [...prev, {
      user_message: input_value,
      bot_response: "",
      created_at: ""
    }])
    setisbotloading(true);
    const reply = await api.post("/query", { query: input_value })
    const res = reply.data.response 

    setChats(prev => {
      const updated = [...prev]
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        bot_response: res,
        created_at: "test"
      }
      return updated
    })

  } catch (e) {
    setInput(input_value)
    setChats(prev => prev.slice(0, -1))  
  }
  finally{
    setisbotloading(false)
  }
}

function handleKeyDown(e:React.KeyboardEvent){
if(e.key=="Enter" && !(e.shiftKey)){
e.preventDefault()
handleSend();
}
}


  return (
<div className="flex items-center justify-center w-screen h-screen">

  <div className="flex flex-col h-[70vh] w-[60vw] border-2 border-solid">
    
    {/* Chat messages - scrollable */}
    <div className="flex-1 bg-gray-100 overflow-y-auto w-full">
      {chats.map((item, index) => (
        <div key={index}>
          <div className="w-[40%] text-wrap ml-auto bg-blue-500 text-white px-4 py-4 mr-1 rounded-tl-lg rounded-tr-lg rounded-bl-lg" >
            {item.user_message}
          </div>
          <div className="w-[40%] text-wrap mr-auto bg-amber-800 text-white px-4 py-2 rounded-tl-lg rounded-tr-lg rounded-br-lg ml-1">
            {isbotloading && index==chats.length-1?"Thinking...":item.bot_response}
          </div>
          <div className="flex flex-row justify-center items-center text-xs">
            {item.created_at}
          </div>
        </div>
      ))}
    </div>

    {/* Input bar */}
<div className="flex w-[70%] mx-auto rounded-3xl border border-gray-300 overflow-hidden items-end mb-2 relative">
  <textarea
    ref={textareaRef}
    placeholder="type your message here..."
    rows={1}
    className="w-[70%] flex-1 px-4 py-2 outline-none resize-none overflow-hidden"
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={(e)=>handleKeyDown(e)}
    value={input}
  />
  <button 
  className=" w-[30%] bg-blue-500 text-white py-2 hover:bg-blue-600"
  onClick={handleSend}
  >
    Send
  </button>
</div>

  </div>

</div>
  )
}