package com.application.KWB.main;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class MainController {

	@GetMapping()  // 홈페이지 메인
	public String main() {
		return "main";
	}
	
}
