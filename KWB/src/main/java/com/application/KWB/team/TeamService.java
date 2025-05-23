package com.application.KWB.team;

import java.util.List;

import org.springframework.stereotype.Service;


public interface TeamService {

	List<HitterDTO> findHitterListByTeam(String teamName);

	List<PitcherDTO> findPitcherListByTeam(String teamName);

}
