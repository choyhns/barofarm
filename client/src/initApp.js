async function waitBackendReady() {
  let ready = false;

  while (!ready) {
    try {
      const res = await fetch("http://localhost:8080/actuator/health/readiness");
      const json = await res.json();
      if (json.status === "UP") {
        ready = true;
        break;
      }
    } catch (e) {
      // 서버 안 켜져 있으면 그냥 대기
    }
    await new Promise(r => setTimeout(r, 1000));
  }
}

export async function initApp() {
  await waitBackendReady();  
} 
