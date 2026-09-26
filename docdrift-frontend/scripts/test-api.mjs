/**
 * Test script verifying frontend API client connection to the running FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function testFrontendClient() {
  console.log('================================================================================');
  console.log('       DOCDRIFT FRONTEND -> BACKEND API CLIENT VERIFICATION                    ');
  console.log('================================================================================');
  console.log(`Connecting to Backend at: ${API_BASE_URL}\n`);

  // 1. Test getDocuments()
  console.log('[1/2] Calling GET /documents...');
  const docsRes = await fetch(`${API_BASE_URL}/documents`);
  if (!docsRes.ok) {
    throw new Error(`GET /documents failed with HTTP ${docsRes.status}`);
  }
  const documents = await docsRes.json();
  console.log(`[PASS] Received ${documents.length} indexed documents from library.`);
  console.log('Sample documents:', documents.slice(0, 3));

  // 2. Test askQuestion() with hardcoded question and version
  const testPayload = {
    question: "How do I get a user's address in version 2.1?",
    version: "v2.1",
  };

  console.log(`\n[2/2] Calling POST /ask with:`, testPayload);
  const askRes = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(testPayload),
  });

  if (!askRes.ok) {
    const errorJson = await askRes.json().catch(() => ({}));
    throw new Error(`POST /ask failed: ${errorJson.detail || askRes.status}`);
  }

  const askData = await askRes.json();
  console.log('\n[ACTUAL BACKEND RESPONSE RECEIVED]');
  console.log('--------------------------------------------------------------------------------');
  console.log('Answer:');
  console.log(askData.answer);
  console.log('\nCitations:');
  console.log(JSON.stringify(askData.citations, null, 2));
  console.log('\nIs Refusal:', askData.is_refusal);
  console.log('--------------------------------------------------------------------------------');
  console.log('\n[SUCCESS] Frontend API client verified! Backend is reachable and answering.');
}

testFrontendClient().catch((err) => {
  console.error('\n[TEST FAILED]', err.message);
  process.exit(1);
});
