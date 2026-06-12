import asyncio, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv
load_dotenv(override=True)
from agents.orchestrator import run_pipeline, get_session
from tools import report_builder

async def test():
    session_id = 'test-pdf-001'
    print('Rodando pipeline...')
    async for event in run_pipeline('SaaS para pequenos restaurantes com IA', session_id):
        if event.startswith('data:'):
            try:
                p = json.loads(event[6:])
                agent = p.get('agent', '')
                status = p.get('status', '')
                data = p.get('data', '')
                if agent in ['market', 'synthesis', 'score', 'pipeline', 'advocate', 'devil', 'mediator']:
                    print(f'  [{agent}] {status} {str(data)[:100] if status == "error" else ""}')
            except:
                pass

    session = get_session(session_id)
    report = session.get('report', '')
    score_raw = session.get('score', '')
    print(f'Report: {len(report)} chars')
    print(f'Score raw: {str(score_raw)[:80]}')

    score = None
    if score_raw:
        try:
            score = json.loads(score_raw) if isinstance(score_raw, str) else score_raw
            print(f'Score parsed: {score}')
        except Exception as e:
            print(f'Score parse error: {e}')

    print('Gerando PDF...')
    try:
        pdf = report_builder.generate_pdf('SaaS para pequenos restaurantes com IA', report, score)
        print(f'PDF OK: {len(pdf)} bytes')
        with open('test_output.pdf', 'wb') as f:
            f.write(pdf)
        print('Salvo em test_output.pdf')
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
