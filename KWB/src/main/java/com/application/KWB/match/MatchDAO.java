package com.application.KWB.match;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

import com.application.KWB.team.HitterDTO;
import com.application.KWB.team.PitcherDTO;

@Mapper
public interface MatchDAO {

	List<GameDto> getGamesByMonth(int month);

	List<HitterDTO> getHitterByTeam(String teamName);

	List<PitcherDTO> getPitcherByTeam(String teamName);

}
