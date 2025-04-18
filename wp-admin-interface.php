<?php
/**
 * Admin page for AI Coding Agent
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}
?>

<div class="wrap ai-coding-agent-wrap">
    <h1>AI Coding Agent</h1>
    
    <div class="ai-coding-agent-tabs">
        <nav class="nav-tab-wrapper">
            <a href="#repository" class="nav-tab nav-tab-active">Repository</a>
            <a href="#coding-assistant" class="nav-tab">Coding Assistant</a>
            <a href="#settings" class="nav-tab">Settings</a>
        </nav>
        
        <div id="repository" class="tab-content active">
            <div class="card">
                <h2>Repository Management</h2>
                <div class="repository-form">
                    <div class="form-group">
                        <label for="repository-path">Repository Path</label>
                        <input type="text" id="repository-path" class="regular-text" placeholder="/path/to/repository">
                        <button id="check-repository" class="button button-primary">Check Repository</button>
                    </div>
                    
                    <div id="repository-status" class="repository-status" style="display: none;">
                        <h3>Repository Status</h3>
                        <div class="repository-info"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="coding-assistant" class="tab-content">
            <div class="card">
                <h2>AI Coding Assistant</h2>
                
                <div class="coding-assistant-interface">
                    <div class="chat-container">
                        <div id="chat-messages" class="chat-messages"></div>
                        
                        <div class="chat-input">
                            <textarea id="user-query" placeholder="Ask coding questions, get debugging help, request code reviews, etc."></textarea>
                            <button id="send-query" class="button button-primary">Send</button>
                        </div>
                    </div>
                    
                    <div class="code-editor">
                        <h3>Code Editor</h3>
                        <textarea id="code-editor" class="code-editor-textarea"></textarea>
                        <div class="editor-controls">
                            <select id="code-language">
                                <option value="python">Python</option>
                                <option value="javascript">JavaScript</option>
                                <option value="php">PHP</option>
                                <option value="java">Java</option>
                                <option value="csharp">C#</option>
                                <option value="cpp">C++</option>
                                <option value="go">Go</option>
                                <option value="rust">Rust</option>
                            </select>
                            <button id="analyze-code" class="button">Analyze Code</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="settings" class="tab-content">
            <div class="card">
                <h2>Settings</h2>
                
                <form id="ai-coding-agent-settings" method="post" action="options.php">
                    <?php
                    settings_fields('ai_coding_agent_settings');
                    do_settings_sections('ai_coding_agent_settings');
                    ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="ai_model">AI Model</label>
                            </th>
                            <td>
                                <select name="ai_coding_agent_settings[ai_model]" id="ai_model">
                                    <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                                    <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                                    <option value="gpt-4">GPT-4</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">
                                <label for="api_key">API Key</label>
                            </th>
                            <td>
                                <input type="password" name="ai_coding_agent_settings[api_key]" id="api_key" class="regular-text">
                                <p class="description">API key for the selected AI model.</p>
                            </td>
                        </tr>
                        <tr>
                            <th scope="row">
                                <label for="max_tokens">Max Tokens</label>
                            </th>
                            <td>
                                <input type="number" name="ai_coding_agent_settings[max_tokens]" id="max_tokens" class="regular-text" value="4000">
                                <p class="description">Maximum tokens for AI responses.</p>
                            </td>
                        </tr>
                    </table>
                    
                    <?php submit_button(); ?>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
    jQuery(document).ready(function($) {
        // Tab navigation
        $('.ai-coding-agent-tabs .nav-tab').on('click', function(e) {
            e.preventDefault();
            
            // Hide all tab content
            $('.tab-content').removeClass('active');
            
            // Remove active class from tabs
            $('.nav-tab').removeClass('nav-tab-active');
            
            // Get tab ID from href
            var tabId = $(this).attr('href');
            
            // Show tab content
            $(tabId).addClass('active');
            
            // Add active class to tab
            $(this).addClass('nav-tab-active');
        });
        
        // Check repository
        $('#check-repository').on('click', function() {
            var repositoryPath = $('#repository-path').val();
            
            if (!repositoryPath) {
                alert('Please enter a repository path');
                return;
            }
            
            $(this).prop('disabled', true).text('Checking...');
            
            $.ajax({
                url: aiCodingAgentParams.apiEndpoint + '/repository-status',
                method: 'GET',
                data: {
                    repository: repositoryPath
                },
                headers: {
                    'X-WP-Nonce': aiCodingAgentParams.nonce
                },
                success: function(response) {
                    $('#check-repository').prop('disabled', false).text('Check Repository');
                    
                    if (response.success) {
                        // Show repository status
                        $('#repository-status').show();
                        
                        // Display repository info
                        var info = response.status;
                        var html = '<p><strong>Active Branch:</strong> ' + info.active_branch + '</p>';
                        html += '<p><strong>Branches:</strong> ' + info.branches.join(', ') + '</p>';
                        html += '<p><strong>Files Count:</strong> ' + info.files_count + '</p>';
                        
                        $('#repository-status .repository-info').html(html);
                    } else {
                        alert('Error: ' + response.message);
                    }
                },
                error: function() {
                    $('#check-repository').prop('disabled', false).text('Check Repository');
                    alert('Error checking repository');
                }
            });
        });
        
        // Send query
        $('#send-query').on('click', function() {
            var query = $('#user-query').val();
            var repositoryPath = $('#repository-path').val();
            
            if (!query) {
                alert('Please enter a query');
                return;
            }
            
            $(this).prop('disabled', true).text('Sending...');
            
            // Add user message to chat
            $('#chat-messages').append('<div class="message user-message"><p>' + query + '</p></div>');
            
            // Clear input
            $('#user-query').val('');
            
            // Scroll to bottom
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
            
            $.ajax({
                url: aiCodingAgentParams.apiEndpoint + '/process-query',
                method: 'POST',
                data: {
                    query: query,
                    repository: repositoryPath
                },
                headers: {
                    'X-WP-Nonce': aiCodingAgentParams.nonce
                },
                success: function(response) {
                    $('#send-query').prop('disabled', false).text('Send');
                    
                    if (response.success) {
                        // Add response to chat
                        $('#chat-messages').append('<div class="message assistant-message"><p>' + response.response + '</p></div>');
                        
                        // Scroll to bottom
                        $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
                    } else {
                        alert('Error: ' + response.message);
                    }
                },
                error: function() {
                    $('#send-query').prop('disabled', false).text('Send');
                    alert('Error processing query');
                }
            });
        });
        
        // Analyze code
        $('#analyze-code').on('click', function() {
            var code = $('#code-editor').val();
            var language = $('#code-language').val();
            
            if (!code) {
                alert('Please enter code to analyze');
                return;
            }
            
            $(this).prop('disabled', true).text('Analyzing...');
            
            $.ajax({
                url: aiCodingAgentParams.apiEndpoint + '/analyze-code',
                method: 'POST',
                data: {
                    code: code,
                    language: language
                },
                headers: {
                    'X-WP-Nonce': aiCodingAgentParams.nonce
                },
                success: function(response) {
                    $('#analyze-code').prop('disabled', false).text('Analyze Code');
                    
                    if (response.success) {
                        // Add analysis to chat
                        $('#chat-messages').append('<div class="message assistant-message"><p><strong>Code Analysis:</strong></p><p>' + response.analysis.content + '</p></div>');
                        
                        // Scroll to bottom
                        $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
                    } else {
                        alert('Error: ' + response.message);
                    }
                },
                error: function() {
                    $('#analyze-code').prop('disabled', false).text('Analyze Code');
                    alert('Error analyzing code');
                }
            });
        });
    });
</script>

<style>
    .ai-coding-agent-tabs {
        margin-top: 20px;
    }
    
    .tab-content {
        display: none;
        padding: 20px;
        background: #fff;
        border: 1px solid #ccc;
        border-top: none;
    }
    
    .tab-content.active {
        display: block;
    }
    
    .card {
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    .repository-status {
        margin-top: 20px;
        padding: 15px;
        background: #f9f9f9;
        border: 1px solid #ddd;
    }
    
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 400px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background: #f9f9f9;
    }
    
    .chat-input {
        display: flex;
        padding: 10px;
        border-top: 1px solid #ddd;
    }
    
    .chat-input textarea {
        flex: 1;
        min-height: 60px;
        margin-right: 10px;
    }
    
    .message {
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 5px;
    }
    
    .user-message {
        background: #e6f7ff;
        border-left: 4px solid #1e88e5;
    }
    
    .assistant-message {
        background: #f0f4c3;
        border-left: 4px solid #7cb342;
    }
    
    .code-editor {
        margin-top: 20px;
    }
    
    .code-editor-textarea {
        width: 100%;
        min-height: 200px;
        font-family: monospace;
        margin-bottom: 10px;
    }
    
    .editor-controls {
        display: flex;
        justify-content: space-between;
    }
</style>
