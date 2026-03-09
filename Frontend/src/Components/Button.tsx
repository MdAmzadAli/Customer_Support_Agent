
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    color?: 'primary' | 'secondary' | 'danger',
}

function Button({children, color='primary',...args}: ButtonProps)
{
    
    const getColor= (color:string)=>
        {
        switch(color){
            case 'primary':
                return 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded';
            case 'secondary':
                return 'bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded';
            case 'danger':
                return 'bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded';
            default:
                return 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded';
        }
    }

    return(
        <button className={getColor(color)} {...args}>
            {children}
        </button>
    )
}

export default Button;