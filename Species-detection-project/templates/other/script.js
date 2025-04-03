// document.addEventListener("DOMContentLoaded", function () {
//     console.log("Script is loaded!");  // ✅ Debugging message

//     const loginForm = document.getElementById('loginForm');
//     const registerForm = document.getElementById('registerForm');

//     //handeling login event
//     if(loginForm){
//     loginForm.addEventListener('submit', async (event) => {
//         event.preventDefault();
//         console.log(" Login form submitted!");  // Debugging

//         const username = document.getElementById('loginUsername').value;
//         const password = document.getElementById('loginPassword').value;

//         console.log("Sending Login Request →", username, password);  // Debugging

//         try {
//             const response = await fetch('http://127.0.0.1:5000/login', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ username, password })
//             });

//             if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);

//             const data = await response.json();
//             document.getElementById('loginMessage').textContent = data.message;
//         } catch (error) {
//             console.error("Login failed:", error);
//             document.getElementById('loginMessage').textContent = "Login failed! Invalid username or password.";
//         }
//     });
// }

//     //handle registration event
//     if(registerForm){
//     registerForm.addEventListener('submit', async (event) => {
//         event.preventDefault();

//         const name = document.getElementById('registerName').value;
//         const username = document.getElementById('registerUsername').value;
//         const password = document.getElementById('registerPassword').value;

//         console.log("Register Request →", name, username, password);  // Debugging

//         try {
//             const response = await fetch('http://127.0.0.1:5000/register', {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify({ name, username, password })
//             });

//             if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);

//             const data = await response.json();
//             document.getElementById('registerMessage').textContent = data.message;
//         } catch (error) {
//             console.error("Registration failed:", error);
//             document.getElementById('registerMessage').textContent = "Registration failed! Try Again";
//         }
//     });
// }
// });

