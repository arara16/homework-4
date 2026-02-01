package com.cryptovault.gateway.factory;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.util.HashMap;
import java.util.Map;

/**
 * Factory Pattern Implementation for creating service configurations
 * Provides centralized service configuration management
 */
@Component
public class ServiceFactory {
    
    @Value("${services.price.url:http://price-service:5001}")
    private String priceServiceUrl;
    
    @Value("${services.ta.url:http://ta-service:5002}")
    private String taServiceUrl;
    
    @Value("${services.prediction.url:http://prediction-service:5003}")
    private String predictionServiceUrl;
    
    private final Map<String, ServiceConfig> serviceConfigs;
    
    public ServiceFactory() {
        this.serviceConfigs = new HashMap<>();
        initializeServiceConfigs();
    }
    
    /**
     * Initialize default service configurations
     */
    private void initializeServiceConfigs() {
        serviceConfigs.put("price-service", new ServiceConfig(priceServiceUrl, 5000, 3));
        serviceConfigs.put("ta-service", new ServiceConfig(taServiceUrl, 5000, 3));
        serviceConfigs.put("prediction-service", new ServiceConfig(predictionServiceUrl, 10000, 5));
    }
    
    /**
     * Get service configuration by service name
     * @param serviceName Name of the service
     * @return Service configuration
     */
    public ServiceConfig getServiceConfig(String serviceName) {
        ServiceConfig config = serviceConfigs.get(serviceName);
        if (config == null) {
            throw new IllegalArgumentException("Unknown service: " + serviceName);
        }
        return config;
    }
    
    /**
     * Create service URL with specific endpoint
     * @param serviceName Name of the service
     * @param endpoint API endpoint
     * @return Complete service URL
     */
    public String createServiceUrl(String serviceName, String endpoint) {
        ServiceConfig config = getServiceConfig(serviceName);
        return config.getBaseUrl() + endpoint;
    }
    
    /**
     * Check if service is healthy
     * @param serviceName Name of the service
     * @return true if service is healthy
     */
    public boolean isServiceHealthy(String serviceName) {
        // Implementation would check service health endpoint
        return true; // Simplified for now
    }
    
    /**
     * Service configuration data class
     */
    public static class ServiceConfig {
        private final String baseUrl;
        private final int timeout;
        private final int retryAttempts;
        
        public ServiceConfig(String baseUrl, int timeout, int retryAttempts) {
            this.baseUrl = baseUrl;
            this.timeout = timeout;
            this.retryAttempts = retryAttempts;
        }
        
        public String getBaseUrl() { return baseUrl; }
        public int getTimeout() { return timeout; }
        public int getRetryAttempts() { return retryAttempts; }
    }
}
