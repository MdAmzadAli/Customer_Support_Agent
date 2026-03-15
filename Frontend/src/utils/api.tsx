import axios from "axios";

const api=axios.create(
    {
        baseURL:"http://localhost:8000",
        // timeout:10000,
        withCredentials: true 
    }
)

api.interceptors.response.use(
    (response)=>response,
    async (error)=>{
        if(error.response?.status==401){
            try{
                await api.get("/user/create");
                return api(error.config)
            }
            catch(refreshError){
               return Promise.reject(refreshError)
            }
        }
        return Promise.reject(error)
    }
)

export default api