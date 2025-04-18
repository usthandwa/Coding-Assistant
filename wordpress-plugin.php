<?php
/**
 * Plugin Name: AI Coding Agent
 * Description: WordPress integration for the AI Coding Agent
 * Version: 0.1.0
 * Author: AI Coding Agent Team
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('AI_CODING_AGENT_VERSION', '0.1.0');
define('AI_CODING_AGENT_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('AI_CODING_AGENT_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include required files
require_once AI_CODING_AGENT_PLUGIN_DIR . 'includes/class-ai-coding-agent.php';
require_once AI_CODING_AGENT_PLUGIN_DIR . 'includes/class-ai-coding-agent-api.php';

/**
 * Main plugin class
 */
class AI_Coding_Agent_Plugin {
    /**
     * Instance of this class
     */
    private static $instance = null;

    /**
     * Plugin instance
     *
     * @return AI_Coding_Agent_Plugin
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Constructor
     */
    private function __construct() {
        // Initialize plugin
        add_action('plugins_loaded', array($this, 'init'));
        
        // Register activation and deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }

    /**
     * Initialize plugin
     */
    public function init() {
        // Initialize API
        new AI_Coding_Agent_API();
        
        // Admin hooks
        if (is_admin()) {
            add_action('admin_menu', array($this, 'add_admin_menu'));
            add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_scripts'));
        }
    }

    /**
     * Plugin activation
     */
    public function activate() {
        // Create necessary database tables if needed
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'ai_coding_agent_sessions';
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            session_id varchar(50) NOT NULL,
            user_id mediumint(9) NOT NULL,
            repository varchar(255) NOT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,
            data longtext NOT NULL,
            PRIMARY KEY  (id),
            UNIQUE KEY session_id (session_id)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }

    /**
     * Plugin deactivation
     */
    public function deactivate() {
        // Clean up if needed
    }

    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_menu_page(
            'AI Coding Agent',
            'AI Coding Agent',
            'manage_options',
            'ai-coding-agent',
            array($this, 'admin_page'),
            'dashicons-editor-code',
            81
        );
    }

    /**
     * Admin page
     */
    public function admin_page() {
        require_once AI_CODING_AGENT_PLUGIN_DIR . 'admin/admin-page.php';
    }

    /**
     * Enqueue admin scripts
     */
    public function enqueue_admin_scripts($hook) {
        if ('toplevel_page_ai-coding-agent' !== $hook) {
            return;
        }
        
        // Enqueue styles and scripts
        wp_enqueue_style('ai-coding-agent-admin', AI_CODING_AGENT_PLUGIN_URL . 'admin/css/admin.css', array(), AI_CODING_AGENT_VERSION);
        wp_enqueue_script('ai-coding-agent-admin', AI_CODING_AGENT_PLUGIN_URL . 'admin/js/admin.js', array('jquery'), AI_CODING_AGENT_VERSION, true);
        
        // Localize script
        wp_localize_script('ai-coding-agent-admin', 'aiCodingAgentParams', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('ai-coding-agent-nonce'),
            'apiEndpoint' => rest_url('ai-coding-agent/v1')
        ));
    }
}

// Initialize the plugin
AI_Coding_Agent_Plugin::get_instance();

/**
 * API class for AI Coding Agent
 */
class AI_Coding_Agent_API {
    /**
     * Constructor
     */
    public function __construct() {
        add_action('rest_api_init', array($this, 'register_routes'));
    }

    /**
     * Register API routes
     */
    public function register_routes() {
        register_rest_route('ai-coding-agent/v1', '/process-query', array(
            'methods' => 'POST',
            'callback' => array($this, 'process_query'),
            'permission_callback' => array($this, 'check_permission')
        ));
        
        register_rest_route('ai-coding-agent/v1', '/repository-status', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_repository_status'),
            'permission_callback' => array($this, 'check_permission')
        ));
        
        register_rest_route('ai-coding-agent/v1', '/analyze-code', array(
            'methods' => 'POST',
            'callback' => array($this, 'analyze_code'),
            'permission_callback' => array($this, 'check_permission')
        ));
    }

    /**
     * Check permission
     */
    public function check_permission() {
        return current_user_can('edit_posts');
    }

    /**
     * Process query
     */
    public function process_query($request) {
        // Get parameters
        $params = $request->get_params();
        
        // Validate parameters
        if (empty($params['query'])) {
            return new WP_Error('missing_query', 'Query is required', array('status' => 400));
        }
        
        // Call Python bridge
        $response = $this->call_python_bridge('process_query', $params);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        // Store session if needed
        if (!empty($response['session_id'])) {
            $this->store_session_data($response['session_id'], $params['repository'] ?? '', $response);
        }
        
        return rest_ensure_response($response);
    }

    /**
     * Get repository status
     */
    public function get_repository_status($request) {
        // Get parameters
        $params = $request->get_params();
        
        // Validate parameters
        if (empty($params['repository'])) {
            return new WP_Error('missing_repository', 'Repository is required', array('status' => 400));
        }
        
        // Call Python bridge
        $response = $this->call_python_bridge('get_repository_status', $params);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        return rest_ensure_response($response);
    }

    /**
     * Analyze code
     */
    public function analyze_code($request) {
        // Get parameters
        $params = $request->get_params();
        
        // Validate parameters
        if (empty($params['code'])) {
            return new WP_Error('missing_code', 'Code is required', array('status' => 400));
        }
        
        if (empty($params['language'])) {
            return new WP_Error('missing_language', 'Language is required', array('status' => 400));
        }
        
        // Call Python bridge
        $response = $this->call_python_bridge('analyze_code', $params);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        return rest_ensure_response($response);
    }

    /**
     * Call Python bridge
     */
    private function call_python_bridge($endpoint, $params) {
        // Get Python script path
        $python_script = AI_CODING_AGENT_PLUGIN_DIR . 'bridge/wp_bridge.py';
        
        if (!file_exists($python_script)) {
            return new WP_Error('bridge_not_found', 'Python bridge not found', array('status' => 500));
        }
        
        // Prepare command
        $command = 'python "' . $python_script . '" --endpoint ' . escapeshellarg($endpoint) . ' --params ' . escapeshellarg(json_encode($params));
        
        // Execute command
        $output = shell_exec($command);
        
        if (empty($output)) {
            return new WP_Error('bridge_error', 'Error communicating with Python bridge', array('status' => 500));
        }
        
        // Parse output
        $response = json_decode($output, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return new WP_Error('bridge_response_error', 'Invalid response from Python bridge', array('status' => 500));
        }
        
        return $response;
    }

    /**
     * Store session data
     */
    private function store_session_data($session_id, $repository, $data) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'ai_coding_agent_sessions';
        
        // Check if session exists
        $existing = $wpdb->get_var($wpdb->prepare(
            "SELECT id FROM $table_name WHERE session_id = %s",
            $session_id
        ));
        
        if ($existing) {
            // Update existing session
            $wpdb->update(
                $table_name,
                array(
                    'updated_at' => current_time('mysql'),
                    'data' => json_encode($data)
                ),
                array('session_id' => $session_id)
            );
        } else {
            // Insert new session
            $wpdb->insert(
                $table_name,
                array(
                    'session_id' => $session_id,
                    'user_id' => get_current_user_id(),
                    'repository' => $repository,
                    'created_at' => current_time('mysql'),
                    'updated_at' => current_time('mysql'),
                    'data' => json_encode($data)
                )
            );
        }
    }
}
