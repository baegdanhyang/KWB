package com.application.KWB.match;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/match")
public class Match{

	@GetMapping("/detail")
	public String register()  {
		return "match/detail";
	}
	
}
