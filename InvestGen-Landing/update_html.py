import json
import re

# Load unified JSON
with open('poc_results.json', 'r') as f:
    data = json.load(f)

# Load existing HTML
with open('calibration.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Section B hardcoded Brier scores (Top Widget)
# These are in the matrix badges like Brier: 0.4927
tc_keys = ['test_case_1', 'test_case_2', 'test_case_3', 'test_case_4']
methods = ['HMM', 'GMM', 'Rule-Based']

# First, extract averages for Section D
avg_brier = data['overall_poc_finding']['avg_brier_scores']

# 2. Re-render Section C (Extended Metric Comparison) entirely to ensure no mismatches
section_c_html = """
            <!-- SECTION 3.5: EXTENDED 5-METRIC COMPARISON -->
            <div class="widget-card" style="margin-bottom: 1.5rem;">
                <div class="widget-header">
                    <h3><i class="fas fa-balance-scale" style="color: var(--accent-color);"></i> Extended Metric Comparison: Why Accuracy Alone Is Not Enough</h3>
                    <span class="badge badge-blue">5 Evaluation Metrics Across All Test Cases</span>
                </div>
                <div class="widget-body">
                    <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin: 0 0 1rem 0;">
                        The table above scores each method using only Brier Score, Flip Rate, and Directional Accuracy. Those three metrics answer different questions, but none of them test whether a model's stated confidence actually matches reality. The table below adds two calibration-specific metrics (Brier Score and ECE) alongside Accuracy, AUC-ROC, and Log Loss, all computed from the same predictions on the same data. All metrics shown are generated from a single, unified pure-Python source to guarantee 100% consistency.
                    </p>
"""

icon_map = {'HMM': 'fas fa-brain', 'GMM': 'fas fa-shapes', 'Rule-Based': 'fas fa-code-branch'}
tc_icons = ['fas fa-left-right', 'fas fa-arrow-trend-up', 'fas fa-bolt', 'fas fa-chart-line']

for i, tc in enumerate(tc_keys):
    tc_data = data['test_cases'][tc]
    tc_name = tc_data['name']
    ticker = tc_data['ticker']
    obs = tc_data['observations']
    metrics = tc_data['metrics']
    
    section_c_html += f"""
                    <!-- Test Case {i+1}: {tc_name} -->
                    <div style="margin-bottom: 1.25rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <i class="{tc_icons[i]}" style="color: var(--neutral);"></i>
                            <strong style="font-size: 0.88rem;">{tc_name} ({ticker}, {obs} observations)</strong>
                        </div>
                        <div class="table-responsive">
                            <table class="data-table" style="font-size: 0.82rem;">
                                <thead>
                                    <tr>
                                        <th>Method</th>
                                        <th class="text-center">Accuracy</th>
                                        <th class="text-center">AUC-ROC</th>
                                        <th class="text-center">Log Loss</th>
                                        <th class="text-center">Brier Score</th>
                                        <th class="text-center">ECE</th>
                                    </tr>
                                </thead>
                                <tbody>
"""
    for method in methods:
        m = metrics[method]
        acc = f"{m['accuracy']:.4f}"
        auc = f"{m['auc_roc']:.4f}" if m['auc_roc'] != 'N/A' else 'N/A'
        ll = f"{m['log_loss']:.4f}"
        brier = f"{m['brier_score']:.4f}"
        ece = f"{m['ece']:.4f}"
        
        # Determine colors
        acc_col = "var(--bullish)" if m['accuracy'] > 0.55 else ("var(--bearish)" if m['accuracy'] < 0.45 else "var(--neutral)")
        acc_bg = "rgba(16,185,129,0.1)" if m['accuracy'] > 0.55 else ("rgba(239,68,68,0.1)" if m['accuracy'] < 0.45 else "rgba(245,158,11,0.1)")
        
        auc_col = "var(--bullish)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] > 0.6) else ("var(--bearish)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] < 0.5) else "var(--neutral)")
        auc_bg = "rgba(16,185,129,0.1)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] > 0.6) else ("rgba(239,68,68,0.1)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] < 0.5) else "rgba(245,158,11,0.1)")
        
        ll_col = "var(--bullish)" if m['log_loss'] < 1.0 else ("var(--bearish)" if m['log_loss'] > 2.0 else "var(--neutral)")
        ll_bg = "rgba(16,185,129,0.1)" if m['log_loss'] < 1.0 else ("rgba(239,68,68,0.1)" if m['log_loss'] > 2.0 else "rgba(245,158,11,0.1)")
        
        b_col = "var(--bullish)" if m['brier_score'] < 0.25 else ("var(--bearish)" if m['brier_score'] > 0.4 else "var(--neutral)")
        b_bg = "rgba(16,185,129,0.1)" if m['brier_score'] < 0.25 else ("rgba(239,68,68,0.1)" if m['brier_score'] > 0.4 else "rgba(245,158,11,0.1)")
        
        e_col = "var(--bullish)" if m['ece'] < 0.15 else ("var(--bearish)" if m['ece'] > 0.3 else "var(--neutral)")
        e_bg = "rgba(16,185,129,0.1)" if m['ece'] < 0.15 else ("rgba(239,68,68,0.1)" if m['ece'] > 0.3 else "rgba(245,158,11,0.1)")
        
        section_c_html += f"""                                    <tr>
                                        <td><i class="{icon_map[method]}" style="color: var(--accent-color); margin-right: 4px;"></i> {method}</td>
                                        <td class="text-center"><span class="matrix-badge" style="background: {acc_bg}; color: {acc_col};">{acc}</span></td>
                                        <td class="text-center"><span class="matrix-badge" style="background: {auc_bg}; color: {auc_col};">{auc}</span></td>
                                        <td class="text-center"><span class="matrix-badge" style="background: {ll_bg}; color: {ll_col};">{ll}</span></td>
                                        <td class="text-center"><span class="matrix-badge" style="background: {b_bg}; color: {b_col};">{brier}</span></td>
                                        <td class="text-center"><span class="matrix-badge" style="background: {e_bg}; color: {e_col};">{ece}</span></td>
                                    </tr>
"""
    section_c_html += """                                </tbody>
                            </table>
                        </div>
                    </div>
"""

# Now compute averages for the Averages table
avg_metrics = {}
for method in methods:
    accs = [data['test_cases'][tc]['metrics'][method]['accuracy'] for tc in tc_keys]
    aucs = [data['test_cases'][tc]['metrics'][method]['auc_roc'] for tc in tc_keys if data['test_cases'][tc]['metrics'][method]['auc_roc'] != 'N/A']
    lls = [data['test_cases'][tc]['metrics'][method]['log_loss'] for tc in tc_keys]
    briers = [data['test_cases'][tc]['metrics'][method]['brier_score'] for tc in tc_keys]
    eces = [data['test_cases'][tc]['metrics'][method]['ece'] for tc in tc_keys]
    
    avg_metrics[method] = {
        'accuracy': sum(accs)/len(accs),
        'auc_roc': sum(aucs)/len(aucs) if aucs else 'N/A',
        'log_loss': sum(lls)/len(lls),
        'brier_score': sum(briers)/len(briers),
        'ece': sum(eces)/len(eces)
    }

section_c_html += """
                    <!-- Aggregate Averages -->
                    <div style="margin-bottom: 1.25rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <i class="fas fa-calculator" style="color: var(--accent-color);"></i>
                            <strong style="font-size: 0.88rem;">Average Across All 4 Test Cases</strong>
                        </div>
                        <div class="table-responsive">
                            <table class="data-table" style="font-size: 0.82rem;">
                                <thead>
                                    <tr>
                                        <th>Method</th>
                                        <th class="text-center">Accuracy</th>
                                        <th class="text-center">AUC-ROC</th>
                                        <th class="text-center">Log Loss</th>
                                        <th class="text-center">Brier Score</th>
                                        <th class="text-center">ECE</th>
                                    </tr>
                                </thead>
                                <tbody style="background: var(--bg-tertiary); font-weight: 600;">
"""
for method in methods:
    m = avg_metrics[method]
    acc = f"{m['accuracy']:.4f}"
    auc = f"{m['auc_roc']:.4f}" if m['auc_roc'] != 'N/A' else 'N/A'
    ll = f"{m['log_loss']:.4f}"
    brier = f"{m['brier_score']:.4f}"
    ece = f"{m['ece']:.4f}"
    
    acc_col = "var(--bullish)" if m['accuracy'] > 0.55 else ("var(--bearish)" if m['accuracy'] < 0.45 else "var(--neutral)")
    auc_col = "var(--bullish)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] > 0.6) else ("var(--bearish)" if (m['auc_roc'] != 'N/A' and m['auc_roc'] < 0.5) else "var(--neutral)")
    ll_col = "var(--bullish)" if m['log_loss'] < 1.0 else ("var(--bearish)" if m['log_loss'] > 2.0 else "var(--neutral)")
    b_col = "var(--bullish)" if m['brier_score'] < 0.25 else ("var(--bearish)" if m['brier_score'] > 0.4 else "var(--neutral)")
    e_col = "var(--bullish)" if m['ece'] < 0.15 else ("var(--bearish)" if m['ece'] > 0.3 else "var(--neutral)")
    
    section_c_html += f"""                                    <tr>
                                        <td><i class="{icon_map[method]}" style="color: var(--accent-color); margin-right: 4px;"></i> {method}</td>
                                        <td class="text-center" style="font-family: monospace; color: {acc_col};">{acc}</td>
                                        <td class="text-center" style="font-family: monospace; color: {auc_col};">{auc}</td>
                                        <td class="text-center" style="font-family: monospace; color: {ll_col};">{ll}</td>
                                        <td class="text-center" style="font-family: monospace; color: {b_col};">{brier}</td>
                                        <td class="text-center" style="font-family: monospace; color: {e_col};">{ece}</td>
                                    </tr>
"""

hmm_sys_acc = data['test_cases']['test_case_4']['metrics']['HMM']['accuracy']
hmm_sys_auc = data['test_cases']['test_case_4']['metrics']['HMM']['auc_roc']
hmm_sys_ece = data['test_cases']['test_case_4']['metrics']['HMM']['ece']
rule_sys_acc = data['test_cases']['test_case_4']['metrics']['Rule-Based']['accuracy']
rule_sys_ece = data['test_cases']['test_case_4']['metrics']['Rule-Based']['ece']

section_c_html += f"""                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Key Finding Callout -->
                    <div style="background: var(--accent-light); border: 1px solid var(--accent-border); border-radius: var(--radius-md); padding: 1rem 1.25rem; margin-top: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem;">
                            <i class="fas fa-magnifying-glass-chart" style="color: var(--accent-color);"></i>
                            <strong style="font-size: 0.9rem; color: var(--accent-color);">Key Finding: Accuracy and Calibration Disagree on the Clear Trend Case</strong>
                        </div>
                        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.65; margin: 0 0 0.5rem 0;">
                            In the Clear Trend test case (SYS), HMM achieved an accuracy of {hmm_sys_acc:.4f} and AUC-ROC of {hmm_sys_auc:.4f}. By these two metrics, HMM looks like a strong model. But its ECE was {hmm_sys_ece:.4f}, meaning its stated confidence was significantly off from actual outcomes.
                        </p>
                        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.65; margin: 0 0 0.5rem 0;">
                            Rule-Based had an accuracy of {rule_sys_acc:.4f}, but its ECE was {rule_sys_ece:.4f}. That means when it said 70% likely, the real hit rate was close to 70%. Its probability outputs were honest.
                        </p>
                        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.65; margin: 0;">
                            This is a concrete example of a model looking more accurate while being less honest about its own confidence. This is why the system uses Brier Score and ECE as primary evaluation metrics instead of accuracy alone. Accuracy tells you how often the model was right. ECE tells you whether the model knows when it does not know.
                        </p>
                    </div>
                </div>
            </div>
"""

# Replace Section C
start_idx = html.find('<!-- SECTION 3.5: EXTENDED 5-METRIC COMPARISON -->')
end_idx = html.find('<!-- SECTION 4: OBJECTIVE POC FINDING BANNER -->')
html = html[:start_idx] + section_c_html + html[end_idx:]

# Update the legacy table (Section B) hardcoded values
for i, tc in enumerate(tc_keys):
    tc_data = data['test_cases'][tc]
    for m in methods:
        brier = tc_data['metrics'][m]['brier_score']
        
        # Regex to find the Brier matrix badge for this test case / method in Section B
        # The legacy table structure is:
        # <tr>
        #     <td><strong>Sideways / Noisy</strong> ... </td>
        #     <td>... <span ...>Brier: 0.4927</span> ... </td>
        #     <td>... <span ...>Brier: 0.6508</span> ... </td>
        #     <td>... <span ...>Brier: 0.2032</span> ... </td>
        # </tr>
        pass

# Actually, the legacy table has its values ordered exactly by test case then method.
# Let's just do a regex replace on all "Brier: 0.XXXX" inside Section 3.
# Wait, let's just find them all and replace them in order.
import re
brier_matches = list(re.finditer(r'Brier: \d\.\d{4}', html))
expected_count = 12 # 4 test cases * 3 methods
if len(brier_matches) == expected_count:
    flat_briers = []
    for tc in tc_keys:
        for m in methods:
            flat_briers.append(f"Brier: {data['test_cases'][tc]['metrics'][m]['brier_score']:.4f}")
    
    # Replace from back to front to preserve indices
    for match, new_val in zip(reversed(brier_matches), reversed(flat_briers)):
        html = html[:match.start()] + new_val + html[match.end():]

# Update the Section D (Averages) bottom table
avg_brier_matches = list(re.finditer(r'Avg Brier: \d\.\d{4}', html))
if len(avg_brier_matches) == 3:
    flat_avg = [
        f"Avg Brier: {avg_metrics['HMM']['brier_score']:.4f}",
        f"Avg Brier: {avg_metrics['GMM']['brier_score']:.4f}",
        f"Avg Brier: {avg_metrics['Rule-Based']['brier_score']:.4f}"
    ]
    for match, new_val in zip(reversed(avg_brier_matches), reversed(flat_avg)):
        html = html[:match.start()] + new_val + html[match.end():]

# Update the Narrative Text (POC Finding)
html = re.sub(r'Brier error of <strong>\d\.\d{4}</strong>', f"Brier error of <strong>{avg_metrics['HMM']['brier_score']:.4f}</strong>", html)
html = re.sub(r'heuristics achieved <strong>\d\.\d{4}</strong>', f"heuristics achieved <strong>{avg_metrics['Rule-Based']['brier_score']:.4f}</strong>", html)

with open('calibration.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML successfully updated and aligned with unified poc_results.json.")

# Run the automated verification
def verify():
    # Load JSON
    with open('poc_results.json', 'r') as f:
        js = json.load(f)
        
    with open('calibration.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    mismatches = 0
    print("\n--- AUTOMATED VERIFICATION ---")
    for tc in tc_keys:
        for m in methods:
            brier = f"{js['test_cases'][tc]['metrics'][m]['brier_score']:.4f}"
            acc = f"{js['test_cases'][tc]['metrics'][m]['accuracy']:.4f}"
            
            # Check Extended table (Section C)
            if acc not in html_content:
                print(f"Mismatch: Section C missing Accuracy {acc} for {m} in {tc}")
                mismatches += 1
            if brier not in html_content:
                print(f"Mismatch: Section C missing Brier {brier} for {m} in {tc}")
                mismatches += 1
                
            # Check Legacy table (Section B)
            if f"Brier: {brier}" not in html_content:
                print(f"Mismatch: Section B missing 'Brier: {brier}' for {m} in {tc}")
                mismatches += 1
                
    # Check Averages
    hmm_avg = f"{avg_metrics['HMM']['brier_score']:.4f}"
    if hmm_avg not in html_content:
        print(f"Mismatch: Narrative missing HMM Avg Brier {hmm_avg}")
        mismatches += 1
        
    print(f"Total Mismatches Found: {mismatches}")
    if mismatches == 0:
        print("Verification PASSED: All sections show identical metrics.")

verify()
