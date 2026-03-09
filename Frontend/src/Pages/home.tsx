import Button from '../Components/Button'
import { useNavigate } from 'react-router-dom'

export default function Home(){
    const navigate=useNavigate();

    return(
        <div className='min-h-screen flex items-center justify-center bg-gray-100'>
            <Button color='danger' onClick={()=>navigate('/talk')}>Talk To Agent Now</Button>
        </div>
    )
}