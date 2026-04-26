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

        // Set styling based on run status
        if (result.run_status === 'TECHNICAL_FAILURE') {
            className += ' technical-failure';
        } else if (result.run_status === 'SHIFT_DETECTED') {
            className += ' shift-detected';
        } else if (result.run_status === 'NO_SHIFT_FOUND') {
            className += ' no-shift';
        }

        messageEl.className = className;

        let content = `<div class="message-content">${this.escapeHtml(result.output)}`;

        // Add appropriate badge based on status
        if (result.run_status === 'SHIFT_DETECTED') {
            content += `
                <div class="shift-badge shift-confirmed">
                    ◉ Framework Shift Confirmed
                </div>
            `;
        } else if (result.run_status === 'NO_SHIFT_FOUND') {
            content += `
                <div class="shift-badge no-shift">
                    ◦ No Shift Found
                </div>
            `;
        } else if (result.run_status === 'TECHNICAL_FAILURE') {
            content += `
                <div class="shift-badge technical-failure">
                    ⚠ Technical Failure
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
        // Handle technical failure
        if (result.run_status === 'TECHNICAL_FAILURE') {
            this.displayTechnicalFailure(result);
            return;
        }

        // Display steps in order
        result.steps.forEach((step, index) => {
            setTimeout(() => {
                this.renderReasoningStep(step, result);
            }, index * 200); // Stagger animations
        });
    }

    displayTechnicalFailure(result) {
        const card = this.createReasoningCard('Technical Failure', 'ERROR');
        card.className += ' technical-failure-card';

        let errorDetails = '';
        if (result.technical_error) {
            errorDetails = `
                <div class="card-field">
                    <div class="field-label">Module</div>
                    <div class="field-value">${this.escapeHtml(result.technical_error.module)}</div>
                </div>
                <div class="card-field">
                    <div class="field-label">Reason</div>
                    <div class="field-value">${this.escapeHtml(result.technical_error.reason)}</div>
                </div>
            `;
        }

        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Status</div>
                    <div class="field-value">The reflection process encountered technical issues and could not complete reliably.</div>
                </div>
                ${errorDetails}
            </div>
        `;

        this.elements.reasoningContent.appendChild(card);
    }

    renderReasoningStep(step, result) {
        let card;

        switch (step.type) {
            case 'frame':
                card = this.renderFrameCard(step.data.frame);
                break;

            case 'socratic_pass':
                card = this.renderSocraticCard(step);
                break;

            case 'shift_check':
                card = this.renderShiftCard(step);
                break;

            case 'memory_summary':
                card = this.renderMemoryCard(step.data.memory, result);
                break;

            case 'technical_failure':
                card = this.renderTechnicalFailureStep(step);
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
                    <div class="field-value">${this.escapeHtml(frame.apparent_decision || 'Not clear')}</div>
                </div>

                ${frame.hidden_tensions && frame.hidden_tensions.length > 0 ? `
                <div class="card-field">
                    <div class="field-label">Hidden Tensions</div>
                    <ul class="field-list">
                        ${frame.hidden_tensions.map(tension => `<li>${this.escapeHtml(tension)}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                ${frame.conflicting_values && frame.conflicting_values.length > 0 ? `
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

                ${frame.missing_factors && frame.missing_factors.length > 0 ? `
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
                    <div class="field-label">Frame Dimension</div>
                    <div class="field-value">${this.escapeHtml(step.data.frame_dimension || 'Unknown')}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">Question</div>
                    <div class="field-value">${this.escapeHtml(step.data.question)}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">New Constraint</div>
                    <div class="field-value">${this.escapeHtml(step.data.new_constraint)}</div>
                </div>

                <div class="card-field">
                    <div class="field-label">Constraints So Far</div>
                    <ul class="field-list">
                        ${step.data.constraints_so_far.map(constraint => `<li>${this.escapeHtml(constraint)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        return card;
    }

    renderShiftCard(step) {
        const card = this.createReasoningCard(`Shift Check ${step.index}`, 'ANALYZE');

        const shiftStatus = step.data.shift_detected ? 'YES' : 'NO';
        const statusColor = step.data.shift_detected ? 'var(--shift-green)' : 'var(--text-secondary)';

        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Shift Detected</div>
                    <div class="field-value" style="color: ${statusColor}; font-weight: 600;">${shiftStatus}</div>
                </div>

                ${step.data.organizing_distinction ? `
                <div class="card-field">
                    <div class="field-label">Organizing Distinction</div>
                    <div class="field-value">${this.escapeHtml(step.data.organizing_distinction)}</div>
                </div>
                ` : ''}

                <div class="card-field">
                    <div class="field-label">Confidence</div>
                    <div class="field-value">${Math.round(step.data.confidence * 100)}%</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${step.data.confidence * 100}%"></div>
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
                    <div class="field-label">Run Status</div>
                    <div class="field-value" style="color: ${this.getStatusColor(result.run_status)}; font-weight: 600;">
                        ${this.getStatusDisplay(result.run_status)}
                    </div>
                </div>

                <div class="card-field">
                    <div class="field-label">Process Summary</div>
                    <div class="field-value">
                        ${result.questions.length} questions asked,
                        ${result.constraints.length} constraints applied,
                        ${result.rejected_frames.length} frames rejected
                    </div>
                </div>

                ${result.organizing_distinction ? `
                <div class="card-field">
                    <div class="field-label">Organizing Distinction</div>
                    <div class="field-value">${this.escapeHtml(result.organizing_distinction)}</div>
                </div>
                ` : ''}
            </div>
        `;

        return card;
    }

    renderTechnicalFailureStep(step) {
        const card = this.createReasoningCard('Technical Failure', 'ERROR');
        card.className += ' technical-failure-card';

        card.innerHTML += `
            <div class="card-content">
                <div class="card-field">
                    <div class="field-label">Module</div>
                    <div class="field-value">${this.escapeHtml(step.data.module)}</div>
                </div>
                <div class="card-field">
                    <div class="field-label">Reason</div>
                    <div class="field-value">${this.escapeHtml(step.data.reason)}</div>
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

    getStatusColor(runStatus) {
        switch (runStatus) {
            case 'SHIFT_DETECTED': return 'var(--shift-green)';
            case 'NO_SHIFT_FOUND': return 'var(--text-secondary)';
            case 'TECHNICAL_FAILURE': return '#e05a5a';
            default: return 'var(--text-secondary)';
        }
    }

    getStatusDisplay(runStatus) {
        switch (runStatus) {
            case 'SHIFT_DETECTED': return '✓ Framework shift achieved';
            case 'NO_SHIFT_FOUND': return '◦ No shift detected';
            case 'TECHNICAL_FAILURE': return '⚠ Technical failure';
            default: return 'Unknown status';
        }
    }

    scrollConversation() {
        this.elements.conversation.scrollTop = this.elements.conversation.scrollHeight;
    }

    showError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'message-bubble assistant technical-failure';
        errorEl.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(message)}
                <div class="shift-badge technical-failure">
                    ⚠ Connection Error
                </div>
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