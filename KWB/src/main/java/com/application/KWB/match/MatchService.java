package com.application.KWB.match;

import java.util.List;

public interface MatchService {

	List<GameDateDto> getMatchesByMonth(int month);

}
