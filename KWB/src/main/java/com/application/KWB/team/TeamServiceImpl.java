package com.application.KWB.team;


import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;


@Service
public class TeamServiceImpl implements TeamService{
	
	@Autowired
	private TeamDAO teamDAO;

	@Override
	public List<HitterDTO> findHitterListByTeam(String teamName) {
        return teamDAO.findHitterListByTeam(teamName);

	}

	@Override
	public List<PitcherDTO> findPitcherListByTeam(String teamName) {
        return teamDAO.findPitcherListByTeam(teamName); 
	}

}
