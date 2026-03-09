import Button from '../Components/Button'
import { useState,useEffect } from 'react'
export default function Talk(){
 const [state, setState] = useState<
  "static" | "listening" | "thinking" | "talking"
>("static");

  const displayText = {
  static: "Talk To Agent",
  listening: "Listening",
  thinking: "Thinking",
  talking: "Talking"
};
    useEffect(()=>{
        if(state==='static') return;

        const interval=setInterval(()=>{
       setState((prev)=>{
        // if(prev==='static') return 'listening';
        if(prev==='listening') return 'thinking';
        if(prev==='thinking') return 'talking';
        if(prev==='talking') return 'static';
        return prev;
       })

    },5000)
    return ()=>clearInterval(interval);
    },[state!=='static'])
    
    const handleClick=()=>{
        if(state==='static'){
           setState('listening');
        }
        else{
            
           setState('static');  
        }
    }
    return(
        <div className='min-h-screen flex flex-col justify-center items-center'>
           
            {<h1 className='text-xl font-bold text-center mt-10'>   {displayText[state]}...
      
    
                
                </h1>}
            <Button color={`${state==='static'?'secondary':'danger'}`} onClick={handleClick}> 
              {state==='static'? 'Start Talking':'Stop Talking'}
            </Button>
        </div>
    )
}