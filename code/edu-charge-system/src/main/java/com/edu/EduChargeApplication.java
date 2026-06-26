package com.edu;

import com.edu.common.config.ChargeProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

/**
 * 教育培训机构教务收费管理系统 · v1 启动类（单体，ADR-001）。
 */
@SpringBootApplication
@EnableConfigurationProperties(ChargeProperties.class)
public class EduChargeApplication {

    public static void main(String[] args) {
        SpringApplication.run(EduChargeApplication.class, args);
    }
}
