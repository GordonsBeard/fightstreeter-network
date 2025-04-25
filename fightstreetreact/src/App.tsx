import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [users, setUsers] = useState([])

  const fetchAPI = async () => {
    const response = await axios.get("http://localhost:5000/roster/")
    setUsers(response.data);
  };

  useEffect(() => {
    fetchAPI();
  }, []);

  return (
    <>
        <ul>
          {
            users.map((user, index) => (
              <li key={index}>{user.player_name}</li>
            ))
          }
        </ul>
    </>
  )
}

export default App
