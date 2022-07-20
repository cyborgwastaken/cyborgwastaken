/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_substr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/23 15:26:57 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/04 15:44:58 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_substr(const char *s, unsigned int start, size_t len)
{
	char	*str;
	size_t	count;

	if (!(str = (char*)malloc(sizeof(char) * len + 1)))
		return (NULL);
	if (!s)
		return (NULL);
	count = 0;
	while (len > 0 && s[start + count] && ft_strlen(s) > start)
	{
		str[count] = s[start + count];
		count++;
		len--;
	}
	str[count] = '\0';
	return (str);
}
