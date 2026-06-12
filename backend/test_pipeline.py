import asyncio, sys, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv
load_dotenv(override=True)

from agents.orchestrator import run_pipeline

async def test():
    t0 = time.time()
    async for event in run_pipeline('app de gestao financeira para MEIs', 'test-123'):
        elapsed = time.time() - t0
        if event.startswith('data:'):
            try:
                p = json.loads(event[6:])
                agent = p.get('agent', '?')
                status = p.get('status', '?')
                data_preview = str(p.get('data', ''))[:60].replace('\n', ' ')
                print(f'+{elapsed:.0f}s [{agent:12}] {status} {data_preview}')
            except Exception as e:
                print(f'+{elapsed:.0f}s [parse error] {e}')
        elif event.strip().startswith(': ping'):
            print(f'+{elapsed:.0f}s [heartbeat]')
    print(f'TOTAL: {time.time()-t0:.1f}s')

asyncio.run(test())
