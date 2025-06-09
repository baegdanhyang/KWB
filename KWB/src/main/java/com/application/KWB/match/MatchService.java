package com.application.KWB.match;

import java.util.List;

import com.application.KWB.team.HitterDTO;
import com.application.KWB.team.PitcherDTO;

public interface MatchService {

	List<GameDateDto> getMatchesByMonth(int month);

	List<HitterDTO> getHitterByTeam(String teamName);

	List<PitcherDTO> getPitcherByTeam(String teamName);

}
