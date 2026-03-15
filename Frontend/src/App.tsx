import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './Pages/home'
import Talk from './Pages/talk'
function App() {

  return (
  
      <Router>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path='/talk' element={<Talk/>}/>
        </Routes>
      </Router>
  
  )
}

export default App
