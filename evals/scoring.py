DIMENSIONS=('goal_fit','evidence_fidelity','channel_fit','testability','measurement','safeguards')

def outcome(scores, critical_flags, structural_ok):
    if len(scores)!=6 or any(type(s) is not int or not 0<=s<=4 for s in scores):
        raise ValueError('Six integer rubric scores from zero to four are required')
    total=round(sum(scores)/24*100,2)
    return {'score':total,'passed':total>=75 and min(scores)>=2 and not critical_flags and structural_ok,
            'dimension_scores':dict(zip(DIMENSIONS,scores)), 'critical_flags':critical_flags,'structural_ok':structural_ok}

def aggregate(records,expected=10):
    if len(records)!=expected:raise ValueError('The suite is incomplete')
    valid=[r['final'] for r in records if r.get('final') is not None]
    return {'cases':expected,'scored_cases':len(valid),'failed_or_unscored_cases':expected-len(valid),
            'passed_cases':sum(r['passed'] for r in valid),
            'pass_rate_pct':round(sum(r['passed'] for r in valid)/expected*100,2),
            'mean_score_all_cases':round(sum(r['score'] for r in valid)/expected,2),
            'mean_score_scored_cases':round(sum(r['score'] for r in valid)/len(valid),2) if valid else None,
            'critical_flag_cases':sum(bool(r['critical_flags']) for r in valid)}
