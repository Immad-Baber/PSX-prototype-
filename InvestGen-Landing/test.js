
        // State Machine & Logic
        const chat = document.getElementById('chat');
        let step = 0;
        let selectedStock = "";

        const stateMachine = [
            // Step 0
            {
                aiMsg: "Hello! I'm your InvestOPak AI assistant. What's your primary investment goal today?",
                options: [
                    { label: "Long-term Growth", nextStep: 1 },
                    { label: "Short-term Trading", nextStep: 1 },
                    { label: "Just Exploring", nextStep: 1 }
                ]
            },
            // Step 1
            {
                aiMsg: "Got it. How would you describe your risk tolerance?",
                options: [
                    { label: "Conservative", nextStep: 2 },
                    { label: "Balanced", nextStep: 2 },
                    { label: "Aggressive", nextStep: 2 }
                ]
            },
            // Step 2 (Special: requires stock input)
            {
                aiMsg: "Which PSX stock would you like to analyze?",
                isStockInput: true
            },
            // Step 3 (Agent Working State then Regime Detection)
            {
                isAgentWorking: true,
                aiMsg: (stock) => `I've detected a Sideways market regime for **${stock}**. Based on this, I recommend RSI, MACD, and Bollinger Bands.`,
                triggerRightPanel: 'activate-base-indicators',
                options: [
                    { label: "Continue with these", nextStep: 5 },
                    { label: "Add more indicators", action: 'show-add-indicators' },
                    { label: "Why these?", action: 'show-why' }
                ]
            },
            // Step 4 (Dummy for explanation + ELI5)
            {
                aiMsg: "RSI and Bollinger Bands are great for identifying overbought/oversold levels in a sideways (range-bound) market, while MACD helps spot momentum shifts.",
                options: [
                    { label: "Simplify this (ELI5)", action: 'show-eli5' },
                    { label: "Continue with these", nextStep: 5 },
                    { label: "Add more indicators", action: 'show-add-indicators' }
                ]
            },
            // Step 5 (Conflicting evidence)
            {
                aiMsg: "Most indicators suggest a positive outlook, but our Disconfirmation Agent found that ADX shows weakening trend strength. Want me to investigate further?",
                triggerRightPanel: 'activate-adx',
                options: [
                    { label: "Yes, investigate", nextStep: 6 },
                    { label: "No, skip", nextStep: 6 }
                ]
            },
            // Step 6 (What-If Scenario)
            {
                aiMsg: "I also noticed high energy prices could impact margins. What if inflation rises next month?",
                options: [
                    { label: "Run 'High Inflation' Scenario", action: 'run-what-if' },
                    { label: "Skip to Final Assessment", nextStep: 7 }
                ]
            },
            // Step 7 (Final Resolution)
            {
                aiMsg: "Alright, here is your final AI assessment:",
                triggerRightPanel: 'finalize',
                showFinalCard: true,
                options: []
            }
        ];

        // Helpers
        let isTyping = false;

        function scrollToBottom() {
            chat.scrollTop = chat.scrollHeight;
        }

        async function typeText(element, text, speed = 15) {
            element.innerHTML = '';
            if(text.includes('<') || text.includes('**') || text.includes('&')) {
                let htmlText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                element.innerHTML = htmlText;
            } else {
                for (let i = 0; i < text.length; i++) {
                    element.innerHTML += text.charAt(i);
                    await new Promise(r => setTimeout(r, speed));
                    scrollToBottom();
                }
            }
        }

        async function showTypingIndicator() {
            const wrap = document.createElement('div');
            wrap.className = 'message ai';
            wrap.id = 'typing-indicator-wrap';
            wrap.innerHTML = `
                <div class="avatar"><i class="fas fa-robot"></i></div>
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            `;
            chat.appendChild(wrap);
            scrollToBottom();
            return new Promise(r => setTimeout(r, 800));
        }

        function removeTypingIndicator() {
            const el = document.getElementById('typing-indicator-wrap');
            if(el) el.remove();
        }

        async function showAgentWorking() {
            const wrap = document.createElement('div');
            wrap.className = 'message ai';
            wrap.style.width = '100%';
            wrap.innerHTML = `
                <div class="avatar"><i class="fas fa-network-wired"></i></div>
                <div class="msg-bubble" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59,130,246,0.3); font-size: 0.85rem;">
                    <div id="ag-1" style="opacity: 0.5; margin-bottom: 4px;"><i class="fas fa-spinner fa-spin"></i> Data Agent: Fetching historicals...</div>
                    <div id="ag-2" style="opacity: 0.5; margin-bottom: 4px; display: none;"><i class="fas fa-spinner fa-spin"></i> Market Context Agent: Detecting regime...</div>
                    <div id="ag-3" style="opacity: 0.5; display: none;"><i class="fas fa-spinner fa-spin"></i> Technical Agent: Optimizing GA parameters...</div>
                </div>
            `;
            chat.appendChild(wrap);
            scrollToBottom();
            
            await new Promise(r => setTimeout(r, 1000));
            document.getElementById('ag-1').innerHTML = '<i class="fas fa-check-circle" style="color:#10b981;"></i> Data Agent: Historicals loaded.';
            document.getElementById('ag-1').style.opacity = '1';
            document.getElementById('ag-2').style.display = 'block';
            scrollToBottom();
            
            await new Promise(r => setTimeout(r, 1200));
            document.getElementById('ag-2').innerHTML = '<i class="fas fa-check-circle" style="color:#10b981;"></i> Market Context Agent: Regime detected.';
            document.getElementById('ag-2').style.opacity = '1';
            document.getElementById('ag-3').style.display = 'block';
            scrollToBottom();
            
            await new Promise(r => setTimeout(r, 1500));
            document.getElementById('ag-3').innerHTML = '<i class="fas fa-check-circle" style="color:#10b981;"></i> Technical Agent: Parameters optimized.';
            document.getElementById('ag-3').style.opacity = '1';
            scrollToBottom();
            await new Promise(r => setTimeout(r, 600));
        }

        async function appendAIMessage(textFnOrString, stateObj) {
            if (isTyping) return; // Prevent concurrent messages
            isTyping = true;
            
            if (stateObj?.isAgentWorking) {
                await showAgentWorking();
            } else {
                await showTypingIndicator();
            }
            removeTypingIndicator();

            const text = typeof textFnOrString === 'function' ? textFnOrString(selectedStock) : textFnOrString;
            
            const wrap = document.createElement('div');
            wrap.className = 'message ai';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
            wrap.appendChild(avatar);

            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';
            wrap.appendChild(bubble);
            chat.appendChild(wrap);

            await typeText(bubble, text);

            if (stateObj?.triggerRightPanel) {
                handleRightPanelTrigger(stateObj.triggerRightPanel);
            }

            if (stateObj?.showFinalCard) {
                appendFinalCard();
            } else if (stateObj?.isStockInput) {
                appendStockInput();
            } else if (stateObj?.options?.length > 0) {
                appendOptions(stateObj.options, stateObj);
            }
            
            scrollToBottom();
            isTyping = false;
        }

        function appendUserMessage(text) {
            const wrap = document.createElement('div');
            wrap.className = 'message user';
            wrap.innerHTML = `
                <div class="avatar"><i class="fas fa-user"></i></div>
                <div class="msg-bubble">${text}</div>
            `;
            chat.appendChild(wrap);
            scrollToBottom();
        }

        function appendOptions(options, stateObj) {
            const container = document.createElement('div');
            container.className = 'quick-replies';
            
            options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = 'qr-btn';
                btn.innerText = opt.label;
                btn.onclick = () => {
                    container.style.display = 'none';
                    appendUserMessage(opt.label);
                    
                    if (opt.nextStep !== undefined) {
                        step = opt.nextStep;
                        setTimeout(() => processStep(), 300);
                    } else if (opt.action === 'show-why') {
                        setTimeout(() => appendAIMessage(stateMachine[4].aiMsg, stateMachine[4]), 300);
                    } else if (opt.action === 'show-eli5') {
                        setTimeout(() => appendAIMessage("Basically, RSI acts like a stretched rubber band—if it's pulled too far down, it might snap back up. Bollinger Bands show the 'walls' of the market, and MACD tells us if the trend is accelerating.", { options: [ { label: "Got it, continue", nextStep: 5 }, { label: "Add more indicators", action: 'show-add-indicators' } ] }), 300);
                    } else if (opt.action === 'show-add-indicators') {
                        appendMultiSelect();
                    } else if (opt.action === 'run-what-if') {
                        setTimeout(() => appendAIMessage("Our RAG Agent found a similar scenario in 2022. High inflation typically squeezes cement margins. Adjusting fundamentals weight by -15%.", { options: [ { label: "Proceed to Final Assessment", nextStep: 7 } ] }), 400);
                    }
                };
                container.appendChild(btn);
            });
            chat.appendChild(container);
            scrollToBottom();
        }

        function appendStockInput() {
            const container = document.createElement('div');
            container.className = 'stock-selector';
            container.innerHTML = `
                <input type="text" id="stock-inp" placeholder="e.g. OGDC, LUCK..." value="LUCK">
                <button id="stock-btn">Analyze</button>
            `;
            chat.appendChild(container);
            scrollToBottom();

            document.getElementById('stock-btn').onclick = () => {
                const val = document.getElementById('stock-inp').value || 'LUCK';
                selectedStock = val.toUpperCase();
                container.style.display = 'none';
                appendUserMessage(`Analyze ${selectedStock}`);
                step = 3;
                setTimeout(() => processStep(), 300);
            };
        }

        function appendMultiSelect() {
            const container = document.createElement('div');
            container.className = 'multi-select-container';
            container.innerHTML = `
                <div class="ms-label">Select indicators to add:</div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <div class="ms-chip" onclick="this.classList.toggle('selected')">ADX</div>
                    <div class="ms-chip" onclick="this.classList.toggle('selected')">ATR</div>
                    <div class="ms-chip" onclick="this.classList.toggle('selected')">OBV</div>
                </div>
                <button class="confirm-btn">Confirm</button>
            `;
            chat.appendChild(container);
            scrollToBottom();

            container.querySelector('.confirm-btn').onclick = () => {
                const selected = Array.from(container.querySelectorAll('.ms-chip.selected')).map(c => c.innerText);
                container.style.display = 'none';
                
                if (selected.length > 0) {
                    appendUserMessage(`Add ${selected.join(', ')}`);
                    selected.forEach(ind => {
                        const chip = document.getElementById('chip-' + ind.toLowerCase());
                        if(chip) chip.classList.add('active');
                    });
                } else {
                    appendUserMessage("Don't add any");
                }
                step = 5;
                setTimeout(() => processStep(), 300);
            };
        }

        function appendFinalCard() {
            const wrap = document.createElement('div');
            wrap.className = 'message ai';
            wrap.style.width = '100%';
            wrap.innerHTML = `
                <div class="avatar" style="visibility: hidden;"></div>
                <div class="final-report-card" style="width: 100%; max-width: 400px; margin-left: 0;">
                    <div class="frc-header">
                        <h4 class="frc-title">${selectedStock} Analysis</h4>
                        <span class="frc-tag">Bullish Outlook</span>
                    </div>
                    <div class="frc-body">
                        <ul>
                            <li>RSI indicates stock is oversold, potential bounce.</li>
                            <li>MACD crossing signal line upwards.</li>
                            <li>Disconfirmation: ADX shows weak trend.</li>
                            <li>What-If: Margins squeezed if inflation rises.</li>
                        </ul>
                    </div>
                    <div class="frc-footer">
                        Decision support only, not financial advice.
                        <div style="margin-top: 10px;">
                            <button onclick="alert('Exporting Investment Memo as PDF...')" style="background: var(--accent-color); color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; width: 100%;"><i class="fas fa-file-pdf"></i> Export Investment Memo (PDF)</button>
                        </div>
                    </div>
                </div>
            `;
            chat.appendChild(wrap);
            scrollToBottom();
        }

        function handleRightPanelTrigger(trigger) {
            if (trigger === 'activate-base-indicators') {
                document.getElementById('regime-badge').classList.add('active');
                setTimeout(() => document.getElementById('chip-rsi').classList.add('active'), 200);
                setTimeout(() => document.getElementById('chip-macd').classList.add('active'), 600);
                setTimeout(() => document.getElementById('chip-bb').classList.add('active'), 1000);
            } else if (trigger === 'activate-adx') {
                document.getElementById('chip-adx').classList.add('active');
                document.querySelector('.chart-line').style.stroke = '#f59e0b';
                document.querySelector('.chart-line').style.filter = 'drop-shadow(0 0 8px rgba(245, 158, 11, 0.4))';
            } else if (trigger === 'finalize') {
                const meter = document.getElementById('conf-meter');
                const val = document.getElementById('conf-val');
                let conf = 0;
                const target = 82; 
                const borderColor = getComputedStyle(document.body).getPropertyValue('--border-color').trim() || '#e2e8f0';
                
                meter.style.background = \`conic-gradient(#10b981 \${target}%, \${borderColor} 0)\`;
                val.style.color = '#10b981';
                
                const interval = setInterval(() => {
                    conf += 2;
                    if(conf >= target) {
                        conf = target;
                        clearInterval(interval);
                    }
                    val.innerText = conf + '%';
                }, 30);
            }
        }

        function processStep() {
            if (step >= stateMachine.length) return;
            const s = stateMachine[step];
            appendAIMessage(s.aiMsg, s);
        }

        // Handle manual typing
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        function handleSend() {
            if (isTyping) return; // don't accept input while AI is typing
            
            const text = chatInput.value.trim();
            if(!text) return;
            
            chatInput.value = '';
            // Hide any active quick replies or stock inputs
            const qrs = document.querySelectorAll('.quick-replies, .stock-selector, .multi-select-container');
            qrs.forEach(el => el.style.display = 'none');
            
            appendUserMessage(text);
            
            // If they typed something manually, just advance to the next logical step in the demo
            if (step === 2) {
                // If it was the stock selection step, treat their text as the stock
                selectedStock = text.toUpperCase();
                step = 3;
            } else {
                // Otherwise just move to next step or a specific step
                // For a robust demo, if they type, we just push them forward
                const currentState = stateMachine[step];
                if (currentState && currentState.options && currentState.options.length > 0) {
                    step = currentState.options[0].nextStep !== undefined ? currentState.options[0].nextStep : step + 1;
                } else {
                    step++;
                }
            }
            
            setTimeout(() => processStep(), 600);
        }

        sendBtn.addEventListener('click', handleSend);
        chatInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') {
                e.preventDefault();
                handleSend();
            }
        });

        // Start Conversation
        setTimeout(() => {
            processStep();
        }, 500);
    