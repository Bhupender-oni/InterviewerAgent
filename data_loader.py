import json
from typing import List, Dict, Any
from config import settings

def load_curriculum() -> List[Dict[str, Any]]:
    """Load curriculum from JSON file."""
    with open(settings.curriculum_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract days list from curriculum structure
    if isinstance(data, dict) and 'days' in data:
        return data['days']
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Curriculum format not recognized")

def load_candidate_profile(candidate_id: str) -> Dict[str, Any]:
    """Load and transform candidate profile into normalized format."""
    with open(settings.candidate_profiles_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats: {"candidates": [...]} and {id: {...}}
    candidates_list = data.get('candidates', []) if isinstance(data, dict) else data
    
    # Find candidate
    candidate_data = None
    if isinstance(candidates_list, list):
        for c in candidates_list:
            if c.get('member', {}).get('id') == candidate_id:
                candidate_data = c
                break
    else:
        # If it's a dict keyed by candidate_id
        candidate_data = candidates_list.get(candidate_id)
    
    if not candidate_data:
        raise ValueError(f"Candidate {candidate_id} not found")
    
    # Normalize to standard format
    if 'member' in candidate_data:  # New format from candidates.json
        missions = candidate_data.get('missions', [])
        completed = [m['day'] for m in missions if m.get('passed') and not m.get('skipped')]
        attempted = {m['day']: m.get('attempts', 1) for m in missions if m.get('passed') or m.get('attempts', 1) > 1}
        skipped = [m['day'] for m in missions if m.get('skipped')]
        signals = [
            f"Commitment: {candidate_data.get('signals', {}).get('commitDays', 0)} days",
            f"Missions completed: {candidate_data.get('signals', {}).get('missionsCompleted', 0)}",
            f"First-try success: {candidate_data.get('signals', {}).get('missionsFirstTry', 0)}",
        ]
        member = candidate_data.get('member', {})
        return {
            'candidate_id': candidate_id,
            'name': member.get('name', 'Candidate'),
            'job_role': member.get('jobRole', 'N/A'),
            'experience': member.get('yearsExperience', 0),
            'completed_days': completed,
            'attempted_days': attempted,
            'skipped_days': skipped,
            'learning_signals': signals,
            'missions': missions,
        }
    else:  # Old format (if used)
        return {
            'candidate_id': candidate_id,
            'name': candidate_data.get('name', 'Candidate'),
            'job_role': candidate_data.get('job_role', 'N/A'),
            'experience': candidate_data.get('experience', 0),
            'completed_days': candidate_data.get('completed_days', []),
            'attempted_days': candidate_data.get('attempted_days', {}),
            'skipped_days': candidate_data.get('skipped_days', []),
            'learning_signals': candidate_data.get('learning_signals', []),
        }

def get_available_candidates() -> List[str]:
    """Get list of all available candidate IDs."""
    with open(settings.candidate_profiles_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    candidates_list = data.get('candidates', []) if isinstance(data, dict) else data
    if isinstance(candidates_list, list):
        return [c['member']['id'] for c in candidates_list if 'member' in c]
    else:
        return list(candidates_list.keys())
