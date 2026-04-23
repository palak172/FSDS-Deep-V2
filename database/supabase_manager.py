# database/supabase_manager.py
from supabase import create_client
from datetime import datetime

class SupabaseManager:
    def __init__(self, url, key):
        """Initialize Supabase connection"""
        self.supabase = create_client(url, key)
    
    def get_employee(self, employee_id):
        """Get employee by ID"""
        result = self.supabase.table('employees')\
            .select('employee_id, full_name, department')\
            .eq('employee_id', employee_id)\
            .eq('is_active', True)\
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def get_active_batch(self):
        """Get active production batch"""
        result = self.supabase.table('production_batches')\
            .select('batch_id, product_name')\
            .eq('status', 'active')\
            .limit(1)\
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def start_work_session(self, employee_id, batch_id):
        """Start a new work session"""
        result = self.supabase.table('work_sessions')\
            .insert({
                'employee_id': employee_id,
                'batch_id': batch_id,
                'session_start': datetime.now().isoformat()
            })\
            .execute()
        
        return result.data[0]['session_id']
    
    def end_work_session(self, session_id, safety_status):
        """End a work session"""
        self.supabase.table('work_sessions')\
            .update({
                'session_end': datetime.now().isoformat(),
                'safety_status_at_end': safety_status
            })\
            .eq('session_id', session_id)\
            .execute()
    
    def log_violation(self, session_id, violation_type, severity, duration):
        """Record a safety violation"""
        self.supabase.table('safety_violations')\
            .insert({
                'session_id': session_id,
                'violation_type': violation_type,
                'severity': severity,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            })\
            .execute()
        
        # Increment violation count
        self.supabase.table('work_sessions')\
            .update({'total_violations': self.supabase.rpc('increment_violations', {'sid': session_id})})\
            .eq('session_id', session_id)\
            .execute()
    
    def get_session_summary(self, session_id):
        """Get session summary with join"""
        result = self.supabase.table('work_sessions')\
            .select('session_start, session_end, total_violations, employees(full_name), production_batches(product_name)')\
            .eq('session_id', session_id)\
            .execute()
        
        if result.data:
            data = result.data[0]
            return {
                'start': data['session_start'],
                'end': data['session_end'],
                'violations': data['total_violations'],
                'employee': data['employees']['full_name'],
                'product': data['production_batches']['product_name']
            }
        return None