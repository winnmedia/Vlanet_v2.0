//  API  

async function testLogin() {
  console.log('===  API   ===\n');
  
  const loginData = {
    email: 'demo@test.com',
    password: 'demo1234'
  };
  
  console.log('1.  :', loginData);
  
  try {
    const response = await fetch('http://localhost:8001/api/users/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData)
    });
    
    const responseData = await response.json();
    
    console.log('\n2.  :', response.status);
    console.log('\n3.  :');
    console.log(JSON.stringify(responseData, null, 2));
    
    if (response.ok) {
      console.log('\n  !');
      console.log('- vridge_session:', responseData.vridge_session ? '' : '');
      console.log('- access token:', responseData.access ? '' : '');
      console.log('- refresh token:', responseData.refresh ? '' : '');
      console.log('- user :', responseData.user ? '' : '');
      
      if (responseData.user) {
        console.log('\n :');
        console.log('- :', responseData.user.email);
        console.log('- :', responseData.user.nickname);
        console.log('- ID:', responseData.user.id);
      }
    } else {
      console.log('\n  :', responseData.message || responseData.detail);
    }
    
  } catch (error) {
    console.error('\n  :', error.message);
  }
  
  console.log('\n===   ===');
}

testLogin();