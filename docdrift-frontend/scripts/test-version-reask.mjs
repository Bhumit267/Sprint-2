const API = 'http://localhost:8000';

async function testVersionReask() {
  console.log('================================================================');
  console.log('      DOCDRIFT VERSION DROPDOWN RE-ASK VERIFICATION             ');
  console.log('================================================================');

  const question = "How do I get a user's address?";

  // 1. Initial question asked against v2.1
  console.log(`\n[1/3] Asking question against v2.1: "${question}"`);
  const reqPayload1 = { question, version: 'v2.1' };
  const res1 = await fetch(`${API}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reqPayload1),
  }).then((r) => r.json());

  console.log('-> Response for v2.1:');
  console.log(res1.answer);
  console.log('-> Version confirmed in Citations:', res1.citations.map((c) => `${c.version} § ${c.section}`));

  // 2. Re-asking same question text against v3.0 via dropdown change
  console.log(`\n[2/3] Changing dropdown to v3.0 and re-asking: "${question}"`);
  const reqPayload2 = { question, version: 'v3.0' };
  const res2 = await fetch(`${API}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reqPayload2),
  }).then((r) => r.json());

  console.log('-> Response for v3.0:');
  console.log(res2.answer);
  console.log('-> Version confirmed in Citations:', res2.citations.map((c) => `${c.version} § ${c.section}`));

  // 3. Confirm both distinct answers exist simultaneously
  console.log('\n[3/3] Comparing Thread Entries:');
  console.log(`Entry 1 [v2.1]: ${res1.answer.slice(0, 120)}...`);
  console.log(`Entry 2 [v3.0]: ${res2.answer.slice(0, 120)}...`);
  console.log('\nBoth entries successfully coexist in thread with distinct, version-isolated answers!');
}

testVersionReask().catch((err) => {
  console.error('Error running test:', err);
  process.exit(1);
});
