package com.application.KWB.team;

import java.io.PrintWriter;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;



import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

@Controller
@RequestMapping("/team")
public class TeamController
{
	@Autowired
	private TeamService teamService;

	@GetMapping("/detail")
	public String register(@RequestParam("team") String teamName, Model model) {
		  // 1. 팀 이름 저장
	    model.addAttribute("teamName", teamName);
	    
	    // 2. 팀에 해당하는 타자 리스트 조회 
	    List<HitterDTO> hitterList = teamService.findHitterListByTeam(teamName);
	    List<PitcherDTO> pitcherList = teamService.findPitcherListByTeam(teamName);
	    
	    System.out.println(pitcherList);
	    
	    // 3. 모델에 담기
	    model.addAttribute("hitterList", hitterList);
	    model.addAttribute("pitcherList", pitcherList);
	    
	    return "team/detail";
	}
	
}
