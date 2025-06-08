package com.application.KWB.match;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;


@Controller
@RequestMapping("/match")
public class MatchController{
	@Autowired
	private MatchService matchService;

	@GetMapping("/detail")
	public String register()  {
		return "match/detail";
	}
	
	@GetMapping("/month")
	@ResponseBody
    public List<GameDateDto> getMatchesByMonth(@RequestParam("month") int month) {
        // 서비스에서 해당 월 경기 데이터 가져오기
		
        List<GameDateDto> gameDates = matchService.getMatchesByMonth(month);
        
        System.out.println(gameDates);

     

        return gameDates;
    }
	
}
