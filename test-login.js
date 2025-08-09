// 로그인 API 직접 테스트

async function testLogin() {
  console.log('=== 로그인 API 테스트 시작 ===\n');
  
  const loginData = {
    email: 'demo@test.com',
    password: 'demo1234'
  };
  
  console.log('1. 로그인 시도:', loginData);
  
  try {
    const response = await fetch('http://localhost:8001/api/users/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData)
    });
    
    const responseData = await response.json();
    
    console.log('\n2. 응답 상태:', response.status);
    console.log('\n3. 응답 데이터:');
    console.log(JSON.stringify(responseData, null, 2));
    
    if (response.ok) {
      console.log('\n✅ 로그인 성공!');
      console.log('- vridge_session:', responseData.vridge_session ? '있음' : '없음');
      console.log('- access token:', responseData.access ? '있음' : '없음');
      console.log('- refresh token:', responseData.refresh ? '있음' : '없음');
      console.log('- user 정보:', responseData.user ? '있음' : '없음');
      
      if (responseData.user) {
        console.log('\n사용자 정보:');
        console.log('- 이메일:', responseData.user.email);
        console.log('- 닉네임:', responseData.user.nickname);
        console.log('- ID:', responseData.user.id);
      }
    } else {
      console.log('\n❌ 로그인 실패:', responseData.message || responseData.detail);
    }
    
  } catch (error) {
    console.error('\n❌ 네트워크 오류:', error.message);
  }
  
  console.log('\n=== 테스트 완료 ===');
}

testLogin();