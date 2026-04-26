/*
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
*/

class ThoughtPartner {
    constructor() {
        this.elements = {
            userInput: document.getElementById('userInput'),
            thinkButton: document.getElementById('thinkButton'),
            conversation: document.getElementById('conversation'),
            reasoningContent: document.getElementById('reasoningContent'),
            btnText: document.querySelector('.btn-text'),
            btnLoader: document.querySelector('.btn-loader')
        };

        this.isProcessing = false;
        this.init();
    }

    init() {
        // Enable input and button once page loads
        this.elements.userInput.disabled = false;
        this.elements.thinkButton.disabled = false;

        // Event listeners
        this.elements.thinkButton.addEventListener('click', () => this.handleThink());
        this.elements.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleThink();
            }
        });

        // Auto-resize textarea
        this.elements.userInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
    }

    autoResizeTextarea() {
        const textarea = this.elements.userInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    async handleThink() {
        const input = this.elements.userInput.value.trim();

        if (!input || this.isProcessing) return;

        this.setProcessingState(true);
        this.addUserMessage(input);
        this.clearReasoningPanel();
        this.showProcessingIndicator();

        try {
            const response = await fetch('/think', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: input })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayResult(result);

        } catch (error) {
            console.error('Error:', error);
            this.showError('Something went wrong. Please try again.');
        } finally {
            this.setProcessingState(false);
            this.elements.userInput.value = '';
            this.autoResizeTextarea();
        }
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        this.elements.userInput.disabled = processing;
        this.elements.thinkButton.disabled = processing;

        if (processing) {
            this.elements.btnText.style.display = 'none';
            this.elements.btnLoader.style.display = 'inline';
        } else {
            this.elements.btnText.style.display = 'inline';
            this.elements.btnLoader.style.display = 'none';
        }
    }

    addUserMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message-bubble user';
        messageEl.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(message)}
            </div>
        `;

        this.elements.conversation.appendChild(messageEl);
        this.scrollConversation();
    }

    displayResult(result) {
        this.hideProcessingIndicator();

        // Add assistant response to conversation
        this.addAssistantMessage(result);

        // Display reasoning in right panel
        this.displayReasoning(result);
    }

    addAssistantMessage(result) {
        const messageEl = document.createElement('div');
        let className = 'message-bubble assistant';

        if (result.mode === 'PROTECTION') {
            className += ' protection';
        } else if (result.shift_detected) {
            className += ' shift-detected';
        }

        messageEl.className = className;

        let content = `<div class="message-content">${this.escapeHtml(result.output)}`;

        if (result.shift_detected) {
            content += `
                <div class="shift-badge">
                    ◉ Framework Shift Confirmed
                </div>
            `;
        }

        // Add protection offer banner for medium risk
        if (result.protection_offer && result.protection_offer.show) {
            content += `
                <div class="protection-banner">
                    <div class="protection-banner-content">
                        <div class="protection-banner-text">
                            ${this.escapeHtml(result.protection_offer.message)}
                        </div>
                        <div class="protection-banner-actions">
                            <button class="protection-btn keep-thinking" onclick="this.parentElement.parentElement.parentElement.style.display='none'">
                                Keep thinking
                            </button>
                            <button class="protection-btn switch-protection" onclick="alert('Protection Mode integration pending')">
                                Switch to Protection Mode
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }

        content += `</div>`;
        messageEl.innerHTML = content;

        this.elements.conversation.appendChild(messageEl);
        this.scrollConversation();
    }

    clearReasoningPanel() {
        this.elements.reasoningContent.innerHTML = '';
    }

    showProcessingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'processing-indicator';
        indicator.innerHTML = `
            <div class="processing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div>Thinking...</div>
        `;

        this.elements.reasoningContent.appendChild(indicator);
    }

    hideProcessingIndicator() {
        const indicator = this.elements.reasoningContent.querySelector('.processing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    displayReasoning(result) {
        if (result.mode === 'PROTECTION') {
            this.displayProtectionReasoning(result);
            return;
        }

        // Display steps in order
        result.steps.forEach((step, index) => {
            setTimeout(() => {
                this.renderReasoningStep(step, result);
            }, index * 200); // Stagger animations
        });
    }

    displayProtectionReasoning(result) {
        const card = this.createReasoningCard('Protection Mode', 'ROUTE');
        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Trigger Keywords</div>
                    <div class="field-value">${result.steps[0].trigger_keywords.join(', ')}</div>
                </div>
                <div class="card-field">
                    <div class="field-label">Mode</div>
                    <div class="field-value">Protection Mode activated - reflection paused</div>
                </div>
            </div>
        `;

        this.elements.reasoningContent.appendChild(card);
    }

    renderReasoningStep(step, result) {
        let card;

        switch (step.type) {
            case 'frame':
                card = this.renderFrameCard(step.frame);
                break;

            case 'socratic_pass':
                card = this.renderSocraticCard(step);
                break;

            case 'shift_check':
                card = this.renderShiftCard(step);
                break;

            case 'memory_summary':
                card = this.renderMemoryCard(step.memory, result);
                break;

            default:
                return;
        }

        if (card) {
            this.elements.reasoningContent.appendChild(card);
        }
    }

    renderFrameCard(frame) {
        const card = this.createReasoningCard('Initial Frame', 'EXTRACT');
        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Stated Problem</div>
                    <div class="field-value">${this.escapeHtml(frame.stated_problem)}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">Apparent Decision</div>
                    <div class="field-value">${this.escapeHtml(frame.apparent_decision)}</div>
                </div>

                ${frame.hidden_tensions.length > 0 ? `
                <div class="card-field">
                    <div class="field-label">Hidden Tensions</div>
                    <ul class="field-list">
                        ${frame.hidden_tensions.map(tension => `<li>${this.escapeHtml(tension)}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                ${frame.conflicting_values.length > 0 ? `
                <div class="card-field">
                    <div class="field-label">Conflicting Values</div>
                    <ul class="field-list">
                        ${frame.conflicting_values.map(value => `<li>${this.escapeHtml(value)}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                ${frame.false_binary ? `
                <div class="card-field">
                    <div class="field-label">False Binary</div>
                    <div class="field-value">${this.escapeHtml(frame.false_binary)}</div>
                </div>
                ` : ''}

                ${frame.missing_factors.length > 0 ? `
                <div class="card-field">
                    <div class="field-label">Missing Factors</div>
                    <ul class="field-list">
                        ${frame.missing_factors.map(factor => `<li>${this.escapeHtml(factor)}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;

        return card;
    }

    renderSocraticCard(step) {
        const card = this.createReasoningCard(`Socratic Pass ${step.index}`, 'QUESTION');
        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Question</div>
                    <div class="field-value">${this.escapeHtml(step.question)}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">New Constraint</div>
                    <div class="field-value">${this.escapeHtml(step.new_constraint)}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">Constraints So Far</div>
                    <ul class="field-list">
                        ${step.constraints_so_far.map(constraint => `<li>${this.escapeHtml(constraint)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        return card;
    }

    renderShiftCard(step) {
        const card = this.createReasoningCard(`Shift Check ${step.index}`, 'ANALYZE');

        const shiftStatus = step.shift_detected ? 'YES' : 'NO';
        const statusColor = step.shift_detected ? 'var(--shift-green)' : 'var(--text-secondary)';

        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Shift Detected</div>
                    <div class="field-value" style="color: ${statusColor}; font-weight: 600;">${shiftStatus}</div>
                </div>

                ${step.organizing_distinction ? `
                <div class="card-field">
                    <div class="field-label">Organizing Distinction</div>
                    <div class="field-value">${this.escapeHtml(step.organizing_distinction)}</div>
                </div>
                ` : ''}

                <div class="card-field">
                    <div class="field-label">Confidence</div>
                    <div class="field-value">${Math.round(step.confidence * 100)}%</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${step.confidence * 100}%"></div>
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    renderMemoryCard(memory, result) {
        const card = this.createReasoningCard('Memory Summary', 'COMPLETE');

        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Initial Frame</div>
                    <div class="field-value">${this.escapeHtml(memory.initial_frame.stated_problem || 'Not captured')}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">Final Frame</div>
                    <div class="field-value">${this.escapeHtml(memory.final_frame || 'No change')}</div>
                </div>

                ${memory.organizing_distinction ? `
                <div class="card-field">
                    <div class="field-label">Organizing Distinction</div>
                    <div class="field-value">${this.escapeHtml(memory.organizing_distinction)}</div>
                </div>
                ` : ''}

                <div class="card-field">
                    <div class="field-label">Process Summary</div>
                    <div class="field-value">
                        ${memory.process_summary.total_socratic_passes} questions asked,
                        ${memory.process_summary.total_constraints} constraints applied,
                        ${memory.process_summary.rejected_frame_count} frames rejected
                    </div>
                </div>

                <div class="card-field">
                    <div class="field-label">Shift Status</div>
                    <div class="field-value" style="color: ${result.shift_detected ? 'var(--shift-green)' : 'var(--text-secondary)'}; font-weight: 600;">
                        ${result.shift_detected ? '✓ Framework shift achieved' : '◦ No shift detected'}
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    createReasoningCard(title, badge) {
        const card = document.createElement('div');
        card.className = 'reasoning-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${title}</div>
                <div class="card-badge">${badge}</div>
            </div>
        `;

        return card;
    }

    scrollConversation() {
        this.elements.conversation.scrollTop = this.elements.conversation.scrollHeight;
    }

    showError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'message-bubble assistant';
        errorEl.innerHTML = `
            <div class="message-content" style="border-color: var(--protection-red);">
                ${this.escapeHtml(message)}
            </div>
        `;

        this.elements.conversation.appendChild(errorEl);
        this.scrollConversation();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThoughtPartner();
});