#!/usr/bin/env python3
"""
Test script for protection routing fixes
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.intake import classify_protection_risk, intake

def test_case(description, input_text, expected_level):
    """Test a specific case and show results"""
    print(f"\n=== {description} ===")
    print(f"Input: {input_text}")

    risk = classify_protection_risk(input_text)
    intake_result = intake(input_text)

    print(f"Risk Level: {risk['level']} (expected: {expected_level})")
    print(f"Route: {intake_result['route']}")
    print(f"Triggers: {risk['triggers']}")
    print(f"Reason: {risk['reason']}")

    success = risk['level'] == expected_level
    print(f"[PASS]" if success else f"[FAIL] - got {risk['level']}, expected {expected_level}")
    return success

def main():
    """Run all test cases"""
    print("Testing Protection Routing - Thought Partner v0.2")
    print("=" * 50)

    tests = []

    # HIGH RISK TESTS
    tests.append(test_case(
        "HIGH RISK: Eviction deadline",
        "My landlord says I have 3 days to leave and they're changing the locks tomorrow.",
        "high"
    ))

    tests.append(test_case(
        "HIGH RISK: Court date",
        "I have a court date tomorrow and I don't know what to do.",
        "high"
    ))

    tests.append(test_case(
        "HIGH RISK: Already sent money",
        "I already sent them the money and now they want more. What do I do?",
        "high"
    ))

    # MEDIUM RISK TESTS
    tests.append(test_case(
        "MEDIUM RISK: Workplace pressure (non-reflection)",
        "My boss is pressuring me to go along with something that feels wrong, but I'm not sure what to do.",
        "medium"
    ))

    tests.append(test_case(
        "MEDIUM RISK: Job loss concern",
        "I think my manager is trying to fire me for reporting safety violations.",
        "medium"
    ))

    # LOW RISK TESTS (reflection overrides medium)
    tests.append(test_case(
        "LOW RISK: Boss issue but reflection request",
        "I'm stuck on something and I don't know what the right move is. My boss has been doing things that feel wrong — not illegal, but definitely not right. Cutting corners, blaming others, and putting pressure on me to go along with it. Part of me feels like I should report it or push back. Another part of me is worried about losing my job or making things worse for myself. I keep going back and forth between 'do the right thing' and 'protect myself,' and I can't tell which one is actually right. How should I think about this?",
        "low"
    ))

    tests.append(test_case(
        "LOW RISK: Life decision",
        "I'm deciding whether to move to a new city and I'm scared I'll regret it.",
        "low"
    ))

    tests.append(test_case(
        "LOW RISK: Career choice",
        "I'm torn between two job offers and don't know how to decide.",
        "low"
    ))

    # SUMMARY
    passed = sum(tests)
    total = len(tests)
    print(f"\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} passed")

    if passed == total:
        print("*** ALL TESTS PASSED! Protection routing is working correctly.")
    else:
        print(f"*** {total - passed} tests failed. Review the logic.")

if __name__ == "__main__":
    main()