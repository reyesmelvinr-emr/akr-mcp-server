#!/usr/bin/env python3
"""
Smoke test for write-ops gating (Phase 2).
Validates that permission checks work correctly.
"""

import os
import sys

sys.path.insert(0, 'src')

from tools.config_utils import ErrorType
from tools.write_operations import _check_write_permissions


def test_default_flag_disabled():
    """Test 1: Verify AKR_ENABLE_WRITE_OPS defaults to false"""
    write_ops_enabled = os.getenv('AKR_ENABLE_WRITE_OPS', 'false').lower() == 'true'
    
    print('[TEST 1] Default AKR_ENABLE_WRITE_OPS')
    print(f'  Value: {os.getenv("AKR_ENABLE_WRITE_OPS", "<not set>")}')
    print(f'  Enabled: {write_ops_enabled}')
    
    if not write_ops_enabled:
        print('  ✓ PASS\n')
        return True
    else:
        print('  ✗ FAIL\n')
        return False


def test_permission_check_deny_default():
    """Test 2: Verify permission denied when allowWrites=False"""
    print('[TEST 2] Permission check with allowWrites=False')
    
    result = _check_write_permissions(False)
    is_permission_error = result and result.get('error_type') == 'PERMISSION_DENIED'
    
    print(f'  Result type: {result.get("error") if result else "None"}')
    print(f'  Error code: {result.get("error_type") if result else "None"}')
    
    if is_permission_error:
        print('  ✓ PASS - correctly denied\n')
        return True
    else:
        print('  ✗ FAIL\n')
        return False


def test_permission_check_env_required():
    """Test 3: Verify permission denied when env flag is off (even with allowWrites=True)"""
    print('[TEST 3] Permission check with allowWrites=True but env flag=false')
    
    # Ensure env flag is explicitly off
    os.environ['AKR_ENABLE_WRITE_OPS'] = 'false'
    
    result = _check_write_permissions(True)
    is_permission_error = result and result.get('error_type') == 'PERMISSION_DENIED'
    
    print(f'  Env flag: {os.getenv("AKR_ENABLE_WRITE_OPS")}')
    print(f'  allowWrites: True')
    print(f'  Result type: {result.get("error") if result else "None"}')
    
    if is_permission_error:
        print('  ✓ PASS - correctly denied (env flag required)\n')
        return True
    else:
        print('  ✗ FAIL\n')
        return False


def test_permission_check_allowed():
    """Test 4: Verify permission allowed when both checks pass"""
    print('[TEST 4] Permission check with allowWrites=True AND env flag=true')
    
    os.environ['AKR_ENABLE_WRITE_OPS'] = 'true'
    
    result = _check_write_permissions(True)
    is_allowed = result is None
    
    print(f'  Env flag: {os.getenv("AKR_ENABLE_WRITE_OPS")}')
    print(f'  allowWrites: True')
    print(f'  Result: {result}')
    
    if is_allowed:
        print('  ✓ PASS - write-ops allowed\n')
        return True
    else:
        print('  ✗ FAIL\n')
        return False


def test_permission_error_type():
    """Test 5: Verify PERMISSION_DENIED error type exists"""
    print('[TEST 5] Verify PERMISSION_DENIED error type')
    
    has_error_type = hasattr(ErrorType, 'PERMISSION_DENIED')
    print(f'  ErrorType.PERMISSION_DENIED exists: {has_error_type}')
    
    if has_error_type:
        print('  ✓ PASS\n')
        return True
    else:
        print('  ✗ FAIL\n')
        return False


if __name__ == '__main__':
    print('=== Phase 2: Write-Ops Gating Smoke Test ===\n')
    
    results = [
        test_default_flag_disabled(),
        test_permission_check_deny_default(),
        test_permission_check_env_required(),
        test_permission_check_allowed(),
        test_permission_error_type(),
    ]
    
    print('=== Summary ===')
    passed = sum(results)
    total = len(results)
    print(f'Tests passed: {passed}/{total}')
    
    if passed == total:
        print('✓ All smoke tests PASSED\n')
        sys.exit(0)
    else:
        print('✗ Some tests FAILED\n')
        sys.exit(1)
